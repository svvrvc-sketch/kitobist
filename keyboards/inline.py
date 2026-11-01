from urllib.parse import quote
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def after_register_inline_keyboard() -> InlineKeyboardMarkup:
    """Ro'yxatdan o'tgach xabar ostida chiquvchi inline tugmalar"""
    keyboard = [
        [InlineKeyboardButton(text="🔗 Mening shaxsiy linkim", callback_data="show_my_link")],
        [InlineKeyboardButton(text="📄 Mening hisobim", callback_data="show_my_account")],
        [InlineKeyboardButton(text="📚 Qo'llanma", callback_data="show_rules")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def share_link_inline_keyboard(bot_username: str, user_id: int, custom_share_text: str = None) -> InlineKeyboardMarkup:
    """Do'stlarga ulashish tugmasi"""
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    
    if custom_share_text:
        clean_text = custom_share_text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "").replace("<code>", "").replace("</code>", "")
        if "{ref_link}" in clean_text:
            share_text = clean_text.replace("{ref_link}", ref_link).strip()
        else:
            share_text = f"{clean_text.strip()}\n\n👉 Ishtirok etish uchun havola:\n{ref_link}"
    else:
        share_text = (
            "🥳 DIQQAT, AJOYIB KONKURS!\n\n"
            "Kitobsevarlar uchun qimmatbaho kitoblar to‘plami sovg‘aga berilmoqda! 📚✨\n\n"
            "🎁 G‘oliblarni kutayotgan kitoblar:\n"
            "🥇 1-o‘rin: «Saodat Asri qissalari» (4 qismli to‘liq to‘plam)\n"
            "🥈 2-o‘rin: «Ko‘zlaringni haromdan saqla»\n"
            "🥉 3-o‘rin: «Devona» — Fotih Duman\n"
            "🏅 4-o‘rin: «1500 yillik mahbuslar»\n"
            "⭐️ 5-o‘rin: «Fotimaning bolasi»\n\n"
            "📖 Qatnashish sharti juda oddiy: Quyidagi havola orqali botga kiring, "
            "shaxsiy taklif havolangizni oling va imkoniyatni qo‘ldan boy bermang! Vaqt chegaralangan, hoziroq boshlang! ⬇️\n\n"
            f"👉 Ishtirok etish uchun havola:\n{ref_link}"
        )
    
    # Telegram rasmiy ulashish havolasi: havola matnning eng pastida chiroyli chiqishi uchun
    encoded_share_url = f"https://t.me/share/url?text={quote(share_text)}"
    
    keyboard = [
        [InlineKeyboardButton(text="🚀 Do'stlarga ulashish", url=encoded_share_url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def channels_check_keyboard(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Majburiy kanallarga a'zolikni tekshirish tugmalari"""
    inline_keyboard = []
    for idx, ch in enumerate(channels, start=1):
        btn_text = f"📢 {ch.get('channel_title', f'Kanal {idx}')}"
        btn_url = ch.get("channel_url", "https://t.me") or "https://t.me"
        if not (btn_url.startswith("http://") or btn_url.startswith("https://") or btn_url.startswith("tg://")):
            btn_url = f"https://{btn_url}"
        inline_keyboard.append([InlineKeyboardButton(text=btn_text, url=btn_url)])
    
    inline_keyboard.append([
        InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")
    ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def admin_channels_keyboard(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Admin kanal boshqaruvi"""
    inline_keyboard = []
    for ch in channels:
        inline_keyboard.append([
            InlineKeyboardButton(text=f"❌ {ch['channel_title']}", callback_data=f"del_channel_{ch['channel_id']}")
        ])
    inline_keyboard.append([
        InlineKeyboardButton(text="➕ Yangi kanal qo'shish", callback_data="add_new_channel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def admin_buttons_list_keyboard() -> InlineKeyboardMarkup:
    """Admin uchun tahrirlanadigan tugmalar ro'yxati"""
    keyboard = [
        [InlineKeyboardButton(text="🔗 Mening shaxsiy linkim", callback_data="edit_btn_link")],
        [
            InlineKeyboardButton(text="🎁 Sovg'alar", callback_data="edit_btn_gifts"),
            InlineKeyboardButton(text="📄 Mening hisobim", callback_data="edit_btn_account")
        ],
        [
            InlineKeyboardButton(text="💡 Shartlar", callback_data="edit_btn_rules"),
            InlineKeyboardButton(text="📊 Reyting", callback_data="edit_btn_rating")
        ],
        [
            InlineKeyboardButton(text="📚 Qo'llanma", callback_data="edit_btn_guide")
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_btn_edit")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
