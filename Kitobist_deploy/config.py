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
CONTEST_NAME = "Farzandimni to‘g‘ri tarbiyalayman"

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
    "🎉 <b>“Farzandimni to‘g‘ri tarbiyalayman”</b> konkursida ishtirok etayotganingizdan mamnunmiz!\n\n"
    "G‘oliblar uchun ajratilgan sovg‘alar bilan tanishing 👇\n\n"
    "🥇 <b>1-o‘rin (1 kishi):</b>\n"
    "“Farzand tarbiyasi” PREMIUM kursida bepul o‘qish (qiymati 1 mln so‘m)\n\n"
    "🥈 <b>2-o‘rin (3 kishi):</b>\n"
    "“Farzand tarbiyasi” kursiga 50% chegirma\n\n"
    "🥉 <b>3-o‘rin (5 kishi):</b>\n"
    "Farzand tarbiyasi bo‘yicha audio dars\n\n"
    "🎁 <b>100+ taklif qilganlarga:</b> “Oila va farzand tarbiyasi” darsliklari\n"
    "🎁 <b>50+ taklif qilganlarga:</b> “Oila” haqida darslik\n"
    "🎁 <b>30+ taklif qilganlarga:</b> bepul audio darslik\n\n"
    "📌 <i>Eslatma: havolani faqat farzand tarbiyasiga qiziquvchi ota-onalar, "
    "bo‘lajak ota-onalar va yosh oilalarga yuboring!</i>\n\n"
    "📅 <b>G‘oliblar 9-noyabr, soat 20:00 da aniqlanadi.</b>"
)

TEXT_RULES = TEXT_GIFTS

TEXT_SHARE_TEMPLATE = (
    "🎉 <b>“Farzandimni to‘g‘ri tarbiyalayman” konkursida ishtirok eting!</b>\n\n"
    "G‘oliblar uchun ajratilgan sovg‘alar va bepul darsliklarni yutib oling! 🎁\n\n"
    "👇 Ishtirok etish uchun pastdagi havolani bosing:\n"
    "{referral_link}"
)
