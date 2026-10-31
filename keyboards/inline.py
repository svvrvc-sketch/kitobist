from urllib.parse import quote
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def after_register_inline_keyboard() -> InlineKeyboardMarkup:
    """Ro'yxatdan o'tgach xabar ostida chiquvchi inline tugmalar (skrinshotdagi kabi)"""
    keyboard = [
        [InlineKeyboardButton(text="🔗 Mening shaxsiy linkim", callback_data="show_my_link")],
        [InlineKeyboardButton(text="📄 Mening hisobim", callback_data="show_my_account")],
        [InlineKeyboardButton(text="📚 Qo'llanma", callback_data="show_rules")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def share_link_inline_keyboard(bot_username: str, user_id: int) -> InlineKeyboardMarkup:
    """Do'stlarga ulashish tugmasi"""
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    share_text = (
        "🎉 “Farzandimni to‘g‘ri tarbiyalayman” tanlovida qatnashing va "
        "qimmatbaho kurslar hamda sovg‘alarni yutib oling! 🎁\n\n"
        "👉 Ishtirok etish havolasi:"
    )
    encoded_share_url = f"https://t.me/share/url?url={quote(ref_link)}&text={quote(share_text)}"
    
    keyboard = [
        [InlineKeyboardButton(text="🚀 Do'stlarga ulashish", url=encoded_share_url)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def channels_check_keyboard(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Majburiy kanallarga a'zolikni tekshirish tugmalari"""
    inline_keyboard = []
    for idx, ch in enumerate(channels, start=1):
        btn_text = f"📢 {ch.get('channel_title', f'Kanal {idx}')}"
        btn_url = ch.get("channel_url", "https://t.me")
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
    """Admin uchun tahrirlanadigan tugmalar ro'yxati (skrinshotdagi kabi)"""
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
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
