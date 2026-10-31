from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni yuborish klaviaturasi"""
    button = KeyboardButton(text="📲 Raqamni ulashish", request_contact=True)
    return ReplyKeyboardMarkup(
        keyboard=[[button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi (admin bo'lsa Admin Panel tugmasi bilan)"""
    keyboard = [
        [
            KeyboardButton(text="🔗 Mening shaxsiy linkim")
        ],
        [
            KeyboardButton(text="🎁 Sovg'alar"),
            KeyboardButton(text="📄 Mening hisobim")
        ],
        [
            KeyboardButton(text="💡 Shartlar"),
            KeyboardButton(text="📊 Reyting")
        ]
    ]

    if is_admin:
        keyboard.append([KeyboardButton(text="🛠 Admin Panel")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Admin boshqaruv menyusi"""
    keyboard = [
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="📢 Xabar yuborish")],
        [KeyboardButton(text="🏆 Top Reyting"), KeyboardButton(text="📢 Majburiy kanallar")],
        [KeyboardButton(text="🎛 Tugmalarni tahrirlash")],
        [KeyboardButton(text="🔙 Asosiy menyu")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
