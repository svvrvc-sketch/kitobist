import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Admin IDs
_admins_str = os.getenv("ADMINS", "")
ADMINS = [int(admin_id.strip()) for admin_id in _admins_str.split(",") if admin_id.strip().isdigit()]

# Required subscription channels (usernames or channel IDs, e.g. ["@kitobist_uz"])
_channels_str = os.getenv("CHANNELS", "")
CHANNELS = [ch.strip() for ch in _channels_str.split(",") if ch.strip()]

# Default Contest texts
CONTEST_NAME = "Kitobist"

TEXT_REQUEST_PHONE = (
    "Juda yaxshi!\n\n"
    "Sizga bog'lana olishimiz uchun pastdagi “📲 Raqamni ulashish” tugmasini "
    "bosib telefon raqamingizni yuboring yoki raqamingizni <b>931234567</b> kabi yozib yuboring."
)

TEXT_REGISTER_SUCCESS = (
    "<b>{full_name}</b> siz tanlovda ishtirok etish uchun muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
    "Siz uchun maxsus link tayyorladik, tanishlaringizni faqat shu link orqali kanalga taklif qiling.\n\n"
    "Buning uchun pastdagi <b>“🔗 Mening shaxsiy linkim”</b> tugmasini bosib maxsus post va link olasiz "
    "va maksimal tanishlarga, guruh va kanallarga tarqatasiz. Siz tashlagan link orqali qo'shilgan har bir "
    "do'stingiz uchun <b>1 ball</b> beriladi.\n\n"
    "Sizga omad tilaymiz!"
)

TEXT_MY_ACCOUNT = (
    "✅ <b>Hozircha taklif qilgan do‘stlaringiz soni:</b> {referral_count}\n\n"
    "🚀 Tanlov yakunigacha siz yanada ko‘proq tanishlaringizni botimizda "
    "ro‘yxatdan o‘tishga taklif qilishingiz mumkin.\n\n"
    "Eng yaxshi sovg‘alar sizni kutmoqda ❤️‍🔥"
)

TEXT_GIFTS = (
    "🥳 <b>DIQQAT, AJOYIB KONKURS!</b>\n\n"
    "Kitobsevarlar uchun qimmatbaho kitoblar to‘plami sovg‘aga berilmoqda! 📚✨\n\n"
    "🎁 <b>G‘oliblarni kutayotgan kitoblar:</b>\n\n"
    "🥇 <b>1-o‘rin:</b> «Saodat Asri qissalari» (4 qismli to‘liq to‘plam)\n"
    "🥈 <b>2-o‘rin:</b> «Ko‘zlaringni haromdan saqla»\n"
    "🥉 <b>3-o‘rin:</b> «Devona» — Fotih Duman\n"
    "🎖 <b>4-o‘rin:</b> «1500 yillik mahbuslar»\n"
    "🎖 <b>5-o‘rin:</b> «Fotimaning bolasi»\n\n"
    "📖 <b>Qatnashish sharti juda oddiy:</b> Pastdagi havolangizni do‘stlaringizga ulashing va ko‘proq ball to‘plang!"
)

TEXT_RULES = TEXT_GIFTS

TEXT_SHARE_TEMPLATE = (
    "🥳 <b>DIQQAT, AJOYIB KONKURS!</b>\n\n"
    "Kitobsevarlar uchun qimmatbaho kitoblar to‘plami sovg‘aga berilmoqda! 📚✨\n\n"
    "🎁 <b>G‘oliblarni kutayotgan kitoblar:</b>\n\n"
    "🥇 <b>1-o‘rin:</b> «Saodat Asri qissalari» (4 qismli to‘liq to‘plam)\n"
    "🥈 <b>2-o‘rin:</b> «Ko‘zlaringni haromdan saqla»\n"
    "🥉 <b>3-o‘rin:</b> «Devona» — Fotih Duman\n"
    "🎖 <b>4-o‘rin:</b> «1500 yillik mahbuslar»\n"
    "🎖 <b>5-o‘rin:</b> «Fotimaning bolasi»\n\n"
    "📖 <b>Qatnashish sharti juda oddiy:</b> Quyidagi havola orqali botga kiring, shaxsiy taklif havolangizni oling va imkoniyatni qo‘ldan boy bermang! ⬇️\n\n"
    "{referral_link}"
)
