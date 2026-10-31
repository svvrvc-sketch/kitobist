import re
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, FSInputFile

from config import (
    ADMINS,
    TEXT_REQUEST_PHONE,
    TEXT_REGISTER_SUCCESS,
    TEXT_MY_ACCOUNT,
    TEXT_GIFTS,
    TEXT_RULES,
    BASE_DIR
)
from database import db
from keyboards import (
    phone_request_keyboard,
    main_menu_keyboard,
    after_register_inline_keyboard,
    share_link_inline_keyboard,
    channels_check_keyboard
)
from utils import check_user_subscriptions

user_router = Router()
BANNER_PATH = BASE_DIR / "assets" / "banner.jpg"

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

def format_phone(phone_str: str) -> str:
    """Telefon raqamni tozalash va standart formatga keltirish"""
    digits = re.sub(r"\D", "", phone_str)
    if len(digits) == 9:
        return f"+998{digits}"
    elif len(digits) == 12 and digits.startswith("998"):
        return f"+{digits}"
    elif len(digits) >= 9:
        return f"+{digits}"
    return ""

async def get_default_banner():
    if BANNER_PATH.exists():
        return FSInputFile(str(BANNER_PATH))
    return None

@user_router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, bot: Bot):
    user = message.from_user
    args = command.args

    # Referrer ID ni aniqlash
    referrer_id = None
    if args:
        clean_arg = args.replace("ref_", "")
        if clean_arg.isdigit():
            possible_ref = int(clean_arg)
            if possible_ref != user.id:
                referrer_id = possible_ref

    # Foydalanuvchini bazaga qo'shish
    await db.add_or_update_user(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
        referrer_id=referrer_id
    )

    # Majburiy obunani tekshirish
    channels = await db.get_channels()
    is_sub, unsubscribed = await check_user_subscriptions(bot, user.id, channels)
    if not is_sub:
        await message.answer(
            "⚠️ <b>Botdan to'liq foydalanish uchun quyidagi kanallarga a'zo bo'ling:</b>",
            reply_markup=channels_check_keyboard(unsubscribed),
            parse_mode="HTML"
        )
        return

    # Foydalanuvchi tasdiqlanganmi?
    db_user = await db.get_user(user.id)
    if db_user and db_user.get("is_verified") == 1:
        await message.answer(
            f"Assalomu alaykum, <b>{user.full_name}</b>!\n"
            "Siz tanlovda muvaffaqiyatli ro'yxatdan o'tgansiz. Quyidagi menyudan foydalanishingiz mumkin 👇",
            reply_markup=main_menu_keyboard(is_admin=is_admin(user.id)),
            parse_mode="HTML"
        )
    else:
        # Telefon raqam so'rash
        await message.answer(
            TEXT_REQUEST_PHONE,
            reply_markup=phone_request_keyboard(),
            parse_mode="HTML"
        )

@user_router.callback_query(F.data == "check_subscription")
async def cb_check_subscription(callback: CallbackQuery, bot: Bot):
    channels = await db.get_channels()
    is_sub, unsubscribed = await check_user_subscriptions(bot, callback.from_user.id, channels)
    if not is_sub:
        await callback.answer("❌ Siz hali barcha kanallarga a'zo bo'lmadingiz!", show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=channels_check_keyboard(unsubscribed))
        except Exception:
            pass
        return

    await callback.message.delete()
    db_user = await db.get_user(callback.from_user.id)
    if db_user and db_user.get("is_verified") == 1:
        await callback.message.answer(
            f"✅ A'zoligingiz tasdiqlandi! Xush kelibsiz, <b>{callback.from_user.full_name}</b>!",
            reply_markup=main_menu_keyboard(is_admin=is_admin(callback.from_user.id)),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            TEXT_REQUEST_PHONE,
            reply_markup=phone_request_keyboard(),
            parse_mode="HTML"
        )

# Telefon raqamni qabul qilish (Kontakt yuborilganda)
@user_router.message(F.contact)
async def process_contact(message: Message, bot: Bot):
    user = message.from_user
    contact = message.contact

    if contact.user_id and contact.user_id != user.id:
        await message.answer(
            "⚠️ Iltimos, faqat o'zingizning telefon raqamingizni yuboring!",
            reply_markup=phone_request_keyboard()
        )
        return

    phone = format_phone(contact.phone_number)
    await complete_registration(message, bot, phone)

# Telefon raqam matn shaklida yozilganda
@user_router.message(F.text.regexp(r"^\+?[0-9\s\-\(\)]{9,15}$"))
async def process_phone_text(message: Message, bot: Bot):
    db_user = await db.get_user(message.from_user.id)
    if db_user and db_user.get("is_verified") == 1:
        return

    phone = format_phone(message.text)
    if not phone or len(phone) < 12:
        await message.answer(
            "⚠️ Telefon raqam noto'g'ri kiritildi.\n"
            "Iltimos, namunadagidek yozing: <b>931234567</b> yoki pastdagi <b>“📲 Raqamni ulashish”</b> tugmasidan foydalaning.",
            reply_markup=phone_request_keyboard(),
            parse_mode="HTML"
        )
        return

    await complete_registration(message, bot, phone)

async def complete_registration(message: Message, bot: Bot, phone: str):
    user = message.from_user
    referrer_id = await db.verify_user_phone(user.id, phone)

    # Taklif qilgan foydalanuvchiga bildirishnoma va +1 ball
    if referrer_id:
        try:
            await bot.send_message(
                chat_id=referrer_id,
                text=(
                    f"🎉 <b>Tabriklaymiz!</b> Sizning havolangiz orqali <b>{user.full_name}</b> "
                    f"botdan muvaffaqiyatli ro'yxatdan o'tdi!\n\n"
                    f"⭐️ Hisobingizga <b>+1 ball</b> qo'shildi!"
                ),
                parse_mode="HTML"
            )
        except Exception:
            pass

    text = TEXT_REGISTER_SUCCESS.format(full_name=user.full_name)
    await message.answer(text, reply_markup=main_menu_keyboard(is_admin=is_admin(user.id)), parse_mode="HTML")
    await message.answer(
        "👇 Havolangizni olish yoki hisobingizni tekshirish uchun quyidagi tugmalardan foydalanishingiz mumkin:",
        reply_markup=after_register_inline_keyboard()
    )

# 🔗 Mening shaxsiy linkim
@user_router.message(F.text == "🔗 Mening shaxsiy linkim")
@user_router.callback_query(F.data == "show_my_link")
async def show_personal_link(event: Message | CallbackQuery, bot: Bot):
    user = event.from_user
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user.id}"

    post = await db.get_button_post("btn_link")
    reply_markup = share_link_inline_keyboard(bot_info.username, user.id)

    if post and (post.get("content_text") or post.get("photo_id")):
        photo_id = post.get("photo_id")
        raw_text = post.get("content_text") or ""
        caption = f"{raw_text}\n\n👉 <b>Sizning shaxsiy taklif havolangiz:</b>\n<code>{ref_link}</code>"

        if isinstance(event, CallbackQuery):
            await event.answer()
            if photo_id:
                await event.message.answer_photo(photo=photo_id, caption=caption, reply_markup=reply_markup, parse_mode="HTML")
            else:
                await event.message.answer(caption, reply_markup=reply_markup, parse_mode="HTML")
        else:
            if photo_id:
                await event.answer_photo(photo=photo_id, caption=caption, reply_markup=reply_markup, parse_mode="HTML")
            else:
                await event.answer(caption, reply_markup=reply_markup, parse_mode="HTML")
        return

    # Standart ko'rinish
    caption = (
        f"{TEXT_GIFTS}\n\n"
        f"👉 <b>Sizning shaxsiy taklif havolangiz:</b>\n"
        f"<code>{ref_link}</code>"
    )
    banner = await get_default_banner()

    if isinstance(event, CallbackQuery):
        await event.answer()
        if banner:
            await event.message.answer_photo(photo=banner, caption=caption, reply_markup=reply_markup, parse_mode="HTML")
        else:
            await event.message.answer(caption, reply_markup=reply_markup, parse_mode="HTML")
    else:
        if banner:
            await event.answer_photo(photo=banner, caption=caption, reply_markup=reply_markup, parse_mode="HTML")
        else:
            await event.answer(caption, reply_markup=reply_markup, parse_mode="HTML")

# 🎁 Sovg'alar
@user_router.message(F.text == "🎁 Sovg'alar")
async def show_gifts(message: Message, bot: Bot):
    bot_info = await bot.get_me()
    post = await db.get_button_post("btn_gifts")

    if post and (post.get("content_text") or post.get("photo_id")):
        photo_id = post.get("photo_id")
        text = post.get("content_text") or ""
        if photo_id:
            await message.answer_photo(photo=photo_id, caption=text, parse_mode="HTML")
        else:
            await message.answer(text, parse_mode="HTML")
        return

    banner = await get_default_banner()
    text = f"{TEXT_GIFTS}\n\n👉 Ishtirok etish: @{bot_info.username}"
    if banner:
        await message.answer_photo(photo=banner, caption=text, parse_mode="HTML")
    else:
        await message.answer(text, parse_mode="HTML")

# 💡 Shartlar
@user_router.message(F.text == "💡 Shartlar")
@user_router.callback_query(F.data == "show_rules")
async def show_rules_handler(event: Message | CallbackQuery, bot: Bot):
    bot_info = await bot.get_me()
    post = await db.get_button_post("btn_rules")

    if post and (post.get("content_text") or post.get("photo_id")):
        photo_id = post.get("photo_id")
        text = post.get("content_text") or ""
        if isinstance(event, CallbackQuery):
            await event.answer()
            if photo_id:
                await event.message.answer_photo(photo=photo_id, caption=text, parse_mode="HTML")
            else:
                await event.message.answer(text, parse_mode="HTML")
        else:
            if photo_id:
                await event.answer_photo(photo=photo_id, caption=text, parse_mode="HTML")
            else:
                await event.answer(text, parse_mode="HTML")
        return

    banner = await get_default_banner()
    text = f"{TEXT_RULES}\n\n👉 Ishtirok etish: @{bot_info.username}"
    if isinstance(event, CallbackQuery):
        await event.answer()
        if banner:
            await event.message.answer_photo(photo=banner, caption=text, parse_mode="HTML")
        else:
            await event.message.answer(text, parse_mode="HTML")
    else:
        if banner:
            await event.answer_photo(photo=banner, caption=text, parse_mode="HTML")
        else:
            await event.answer(text, parse_mode="HTML")

# 📄 Mening hisobim
@user_router.message(F.text == "📄 Mening hisobim")
@user_router.callback_query(F.data == "show_my_account")
async def show_account(event: Message | CallbackQuery):
    user = event.from_user
    db_user = await db.get_user(user.id)
    points = db_user.get("points", 0) if db_user else 0
    ref_count = await db.get_referral_count(user.id)

    post = await db.get_button_post("btn_account")
    if post and (post.get("content_text") or post.get("photo_id")):
        photo_id = post.get("photo_id")
        raw_text = post.get("content_text") or ""
        if "{referral_count}" in raw_text:
            text = raw_text.format(referral_count=ref_count, points=points)
        else:
            text = f"{raw_text}\n\n✅ <b>Hozircha taklif qilgan do‘stlaringiz soni:</b> {ref_count}"

        if isinstance(event, CallbackQuery):
            await event.answer()
            if photo_id:
                await event.message.answer_photo(photo=photo_id, caption=text, parse_mode="HTML")
            else:
                await event.message.answer(text, parse_mode="HTML")
        else:
            if photo_id:
                await event.answer_photo(photo=photo_id, caption=text, parse_mode="HTML")
            else:
                await event.answer(text, parse_mode="HTML")
        return

    text = TEXT_MY_ACCOUNT.format(referral_count=ref_count, points=points)
    if isinstance(event, CallbackQuery):
        await event.answer()
        await event.message.answer(text, parse_mode="HTML")
    else:
        await event.answer(text, parse_mode="HTML")

# 📊 Reyting
@user_router.message(F.text == "📊 Reyting")
async def show_rating(message: Message):
    post = await db.get_button_post("btn_rating")
    
    top_users = await db.get_top_rankings(limit=10)
    
    if not top_users:
        no_users_text = "❌ <b>Hozircha reytingda faol foydalanuvchilar mavjud emas.</b>"
        if post and post.get("photo_id"):
            await message.answer_photo(photo=post["photo_id"], caption=no_users_text, parse_mode="HTML")
        else:
            await message.answer(no_users_text, parse_mode="HTML")
        return

    medals = ["🥇", "🥈", "🥉"]
    lines = ["📊 <b>Eng ko'p do'stlarini taklif qilgan faollar (TOP-10):</b>\n"]

    for idx, u in enumerate(top_users, start=1):
        icon = medals[idx - 1] if idx <= 3 else f"{idx}."
        name = u.get("full_name") or "Ishtirokchi"
        clean_name = name.replace("<", "&lt;").replace(">", "&gt;")
        lines.append(f"{icon} <b>{clean_name}</b> — {u['points']} ta taklif")

    user_rank = await db.get_user_rank(message.from_user.id)
    db_user = await db.get_user(message.from_user.id)
    user_points = db_user.get("points", 0) if db_user else 0

    if user_rank:
        lines.append(f"\n⭐️ <b>Sizning ko'rsatkichingiz:</b> {user_points} ta taklif ({user_rank}-o'rin)")
    else:
        lines.append(f"\n⭐️ <b>Sizning ko'rsatkichingiz:</b> {user_points} ta taklif")

    rating_text = "\n".join(lines)
    
    if post and post.get("photo_id"):
        caption = f"{post.get('content_text', '')}\n\n{rating_text}".strip()
        await message.answer_photo(photo=post["photo_id"], caption=caption, parse_mode="HTML")
    else:
        await message.answer(rating_text, parse_mode="HTML")

