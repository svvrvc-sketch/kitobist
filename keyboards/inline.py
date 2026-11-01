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

def share_link_inline_keyboard(bot_username: str, user_id: int, custom_share_text: str = None) -> InlineKeyboardMarkup:
    """Do'stlarga ulashish tugmasi"""
    ref_link = f"https://t.me/{bot_username}?start={user_id}"
    
    if custom_share_text:
        clean_text = custom_share_text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "").replace("<code>", "").replace("</code>", "")
        # Agar matnda ref_link bo'lsa uni olib tashlaymiz, chunki Telegram url parametrida o'zi pastga qo'shadi
        share_text = clean_text.replace("{ref_link}", "").strip()
    else:
        share_text = (
            "🥳 DIQQAT XUSHXABAR❗️\n"
            "Kitobist kanalida kitob sovg‘ali konkurs! 📚🎁\n\n"
            "SOVG'ALAR 😇\n"
            "🥇 1-o‘rin: «Saodat Asri» (4 qismli to‘liq to‘plam)\n"
            "🥈 2-o‘rin: «Ko‘zlaringni haromdan saqla»\n"
            "🥉 3-o‘rin: «Devona» — Fotih Duman\n"
            "🏅 4-o‘rin: «1500 yillik mahbuslar»\n"
            "⭐️ 5-o‘rin: «Fotimaning bolasi»\n\n"
            "📖 Shartlar juda oddiy! Pastdagi havola orqali botga o‘tib, start bosing va ishtirok eting! ⬇️"
        )
    
    # Standart va 100% ishlaydigan Telegram share URL formati
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
