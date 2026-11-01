import asyncio
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import ADMINS
from database import db
from keyboards import (
    admin_menu_keyboard,
    main_menu_keyboard,
    admin_channels_keyboard,
    admin_buttons_list_keyboard
)

admin_router = Router()

BUTTON_NAMES = {
    "btn_link": "🔗 Mening shaxsiy linkim",
    "btn_gifts": "🎁 Sovg'alar",
    "btn_account": "📄 Mening hisobim",
    "btn_rules": "💡 Shartlar",
    "btn_guide": "📚 Qo'llanma",
    "btn_rating": "📊 Reyting"
}

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_channel_id = State()
    waiting_for_channel_title = State()
    waiting_for_channel_url = State()
    waiting_for_button_post = State()

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

@admin_router.message(Command("admin"))
@admin_router.message(F.text == "🛠 Admin Panel")
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Siz admin emassiz!")
        return

    await message.answer(
        "🛠 <b>Admin boshqaruv paneliga xush kelibsiz!</b>\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=admin_menu_keyboard(),
        parse_mode="HTML"
    )

@admin_router.message(F.text == "🔙 Asosiy menyu")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Asosiy menyu:", reply_markup=main_menu_keyboard(is_admin=True))

# 📊 Statistika
@admin_router.message(F.text == "📊 Statistika")
async def show_stats(message: Message):
    if not is_admin(message.from_user.id):
        return

    stats = await db.get_stats()
    text = (
        "📊 <b>Botning umumiy statistikasi:</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']} ta\n"
        f"📱 <b>Raqami tasdiqlanganlar:</b> {stats['verified_users']} ta\n"
        f"🔗 <b>Jami takliflar (referallar):</b> {stats['total_referrals']} ta\n"
        f"📅 <b>Bugun qo'shilganlar:</b> {stats['today_users']} ta"
    )
    await message.answer(text, parse_mode="HTML")

# 🏆 Top Reyting
@admin_router.message(F.text == "🏆 Top Reyting")
async def show_admin_ranking(message: Message):
    if not is_admin(message.from_user.id):
        return

    top_users = await db.get_top_rankings(limit=25)
    if not top_users:
        await message.answer("❌ Hozircha reytingda ball to'plagan foydalanuvchilar yo'q.")
        return

    lines = ["🏆 <b>Top 25 Yetakchilar ro'yxati:</b>\n"]
    for idx, u in enumerate(top_users, start=1):
        username_str = f"(@{u['username']})" if u.get('username') else ""
        lines.append(f"{idx}. <b>{u['full_name']}</b> {username_str} — <b>{u['points']} ball</b> [ID: <code>{u['user_id']}</code>]")

    await message.answer("\n".join(lines), parse_mode="HTML")

# 📢 Xabar yuborish (Rassilka)
@admin_router.message(F.text == "📢 Xabar yuborish")
async def start_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.set_state(AdminStates.waiting_for_broadcast)
    await message.answer(
        "📝 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring (matn, rasm, video yoki post):\n\n"
        "<i>Bekor qilish uchun /cancel buyrug'ini yuboring.</i>",
        parse_mode="HTML"
    )

@admin_router.message(Command("cancel"))
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_menu_keyboard())

@admin_router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Rassilka bekor qilindi.", reply_markup=admin_menu_keyboard())
        return

    await state.clear()
    user_ids = await db.get_all_user_ids()

    status_msg = await message.answer(f"⏳ Xabar {len(user_ids)} ta foydalanuvchiga yuborilmoqda...")
    success = 0
    failed = 0

    for uid in user_ids:
        try:
            await message.copy_to(chat_id=uid)
            success += 1
            await asyncio.sleep(0.04)
        except Exception:
            failed += 1
            await db.set_blocked(uid, is_blocked=1)

    await status_msg.edit_text(
        f"✅ <b>Xabar tarqatish yakunlandi!</b>\n\n"
        f"🟢 Muvaffaqiyatli: {success} ta\n"
        f"🔴 Yetib bormadi (bloklagan): {failed} ta",
        parse_mode="HTML"
    )

# 📢 Majburiy kanallar boshqaruvi
@admin_router.message(F.text == "📢 Majburiy kanallar")
async def manage_channels(message: Message):
    if not is_admin(message.from_user.id):
        return

    channels = await db.get_channels()
    text = (
        "📢 <b>Majburiy a'zo bo'lish kanallari ro'yxati:</b>\n\n"
        "Kanalni o'chirish uchun uning ustiga bosing yoki yangi kanal qo'shing:"
    )
    await message.answer(text, reply_markup=admin_channels_keyboard(channels), parse_mode="HTML")

@admin_router.callback_query(F.data.startswith("del_channel_"))
async def cb_del_channel(callback: CallbackQuery):
    channel_id = callback.data.replace("del_channel_", "")
    await db.delete_channel(channel_id)
    await callback.answer("✅ Kanal o'chirildi!", show_alert=True)
    channels = await db.get_channels()
    await callback.message.edit_reply_markup(reply_markup=admin_channels_keyboard(channels))

@admin_router.callback_query(F.data == "add_new_channel")
async def cb_add_channel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_channel_id)
    await callback.message.answer(
        "Kanalning username yoki ID sini kiriting (masalan: <b>@kanal_username</b> yoki <b>-100123456789</b>):\n"
        "<i>Eslatma: Bot ushbu kanalda administrator bo'lishi shart!</i>\n\n"
        "<i>Bekor qilish: /cancel</i>",
        parse_mode="HTML"
    )

@admin_router.message(AdminStates.waiting_for_channel_id)
async def process_ch_id(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_menu_keyboard())
        return
    await state.update_data(channel_id=message.text.strip())
    await state.set_state(AdminStates.waiting_for_channel_title)
    await message.answer("Kanal nomini kiriting (tugmada ko'rinadigan nom, masalan: <b>Rasmiy Kanal</b>):", parse_mode="HTML")

@admin_router.message(AdminStates.waiting_for_channel_title)
async def process_ch_title(message: Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_menu_keyboard())
        return
    await state.update_data(channel_title=message.text.strip())
    await state.set_state(AdminStates.waiting_for_channel_url)
    await message.answer("Kanalga kirish havolasini kiriting (masalan: <b>https://t.me/kanal_username</b>):", parse_mode="HTML")

@admin_router.message(AdminStates.waiting_for_channel_url)
async def process_ch_url(message: Message, state: FSMContext, bot: Bot):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=admin_menu_keyboard())
        return
    data = await state.get_data()
    channel_id = data["channel_id"]
    channel_title = data["channel_title"]
    channel_url = message.text.strip()

    # Bot kanal admini ekanligini tekshirish
    warning = ""
    try:
        from utils.subscription import format_channel_id
        formatted_id = format_channel_id(channel_id)
        member = await bot.get_chat_member(chat_id=formatted_id, user_id=bot.id)
        if member.status not in ["administrator", "creator"]:
            warning = "\n\n⚠️ <b>DIQQAT:</b> Bot bu kanalda administrator emas! Foydalanuvchilar a'zoligini tekshirish uchun botni kanalda administrator qilishingiz shart!"
    except Exception as e:
        warning = f"\n\n⚠️ <b>DIQQAT:</b> Bot kanalni tekshira olmadi ({e}). Botni ushbu kanalda administrator qilganingizga ishonch hosil qiling!"

    await db.add_channel(channel_id, channel_title, channel_url)
    await state.clear()
    await message.answer(
        f"✅ <b>{channel_title}</b> kanali muvaffaqiyatli qo'shildi!{warning}",
        reply_markup=admin_menu_keyboard(),
        parse_mode="HTML"
    )

# 🎛 Tugmalarni tahrirlash menyusi
@admin_router.message(F.text == "🎛 Tugmalarni tahrirlash")
async def show_buttons_to_edit(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🎛 <b>Tahrirlamoqchi bo'lgan tugmangizni tanlang:</b>\n\n"
        "Tugmani tanlaganingizdan so'ng, foydalanuvchilar o'sha tugmani bosganda chiqadigan yangi postni "
        "(matn yoki rasm + matn) yuborishingiz mumkin bo'ladi 👇",
        reply_markup=admin_buttons_list_keyboard(),
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("edit_btn_"))
async def cb_select_button(callback: CallbackQuery, state: FSMContext):
    btn_key = callback.data.replace("edit_", "")
    btn_name = BUTTON_NAMES.get(btn_key, btn_key)
    
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_button_post)
    await state.update_data(current_button_key=btn_key, current_button_name=btn_name)

    await callback.message.answer(
        f"📝 <b>“{btn_name}”</b> tugmasi uchun yangi postni yuboring.\n\n"
        f"💡 <i>Siz shunchaki oddiy matn yoki rasm + tagidagi matn (caption) shaklida post yuborishingiz mumkin!</i>\n\n"
        f"❌ Bekor qilish uchun: /cancel",
        parse_mode="HTML"
    )

@admin_router.message(AdminStates.waiting_for_button_post, F.text == "/cancel")
async def cancel_edit_button(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Tahrirlash bekor qilindi.", reply_markup=admin_menu_keyboard())

# Post qabul qilish (Rasm yoki Matn)
@admin_router.message(AdminStates.waiting_for_button_post)
async def process_new_button_post(message: Message, state: FSMContext):
    data = await state.get_data()
    btn_key = data.get("current_button_key")
    btn_name = data.get("current_button_name", "Tugma")

    if not btn_key:
        await state.clear()
        await message.answer("Xatolik yuz berdi. Qaytadan urinib ko'ring.", reply_markup=admin_menu_keyboard())
        return

    photo_id = None
    content_text = ""

    if message.photo:
        photo_id = message.photo[-1].file_id
        # Aiogram da message.html_text caption formatini ham saqlaydi
        content_text = message.html_text or message.caption or ""
    elif message.text:
        content_text = message.html_text or message.text

    # Bazaga saqlash
    await db.set_button_post(button_key=btn_key, photo_id=photo_id, content_text=content_text)
    await state.clear()

    await message.answer(
        f"✅ <b>“{btn_name}”</b> bo'limi uchun post muvaffaqiyatli yangilandi!\n\n"
        f"Endi foydalanuvchilar ushbu tugmani bosganlarida quyidagi post ko'rinadi 👇",
        parse_mode="HTML"
    )

    # Adminga namunani ko'rsatish
    if photo_id:
        await message.answer_photo(
            photo=photo_id,
            caption=content_text,
            reply_markup=admin_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            content_text or "<i>(Matnsiz)</i>",
            reply_markup=admin_menu_keyboard(),
            parse_mode="HTML"
        )
