# 📚 Kitobist — Telegram Konkurs & Referal Boti

Telegram orqali kitobxonlik va konkurslar uchun maxsus ishlab chiqilgan, Aiogram 3.x asosidagi professional referal boti.

---

## 🌟 Asosiy Imkoniyatlar

1. **📲 Telefon raqam orqali xavfsiz ro'yxatdan o'tish:**
   - Foydalanuvchi "📲 Raqamni ulashish" orqali yoki qo'lda raqamini kiritadi.
   - Faqat haqiqiy foydalanuvchilar tasdiqlanganda taklif qiluvchiga **+1 ball** beriladi (soxta hisoblar va firibgarlikdan himoyalangan).
2. **🔗 Shaxsiy Referal Havola:**
   - Har bir foydalanuvchi uchun unikal havola: `https://t.me/bot_username?start=USER_ID`.
   - Maxsus dizayndagi banner rasmi va konkurs haqida to'liq post taqdim etiladi.
   - Do'stlarga bir klikda ulashish (Share) inline tugmasi.
3. **🎁 Sovg'alar & 💡 Shartlar:**
   - Konkurs sovrinlari, bosqichlar va qoidalar ko'rsatilgan chiroyli bo'limlar.
4. **📄 Mening hisobim:**
   - Taklif qilingan do'stlar soni va yig'ilgan jami ballar statistikasi.
5. **📊 Reyting (TOP-10):**
   - Eng ko'p ball to'plagan yetakchi ishtirokchilar reytingi va foydalanuvchining o'z o'rni.
6. **📢 Majburiy obuna (Sponsor kanallar):**
   - Konkursda qatnashish uchun kanallarga a'zo bo'lishni tekshirish tizimi.
7. **🛠 Admin Panel (`/admin`):**
   - Bot statistikasi (Jami a'zolar, tasdiqlanganlar, jami takliflar, bugun qo'shilganlar).
   - Barcha foydalanuvchilarga xabar yuborish (Rassilka / Broadcast).
   - Majburiy kanallarni botning o'zidan qo'shish va o'chirish.
   - Yetakchilar reytingini ID lari bilan to'liq ko'rish.

---

## 🚀 Ishga tushirish bo'yicha qo'llanma

### 1. Sozlamalar (`.env`)
Loyihaning ildiz papkasidagi `.env` faylini oching:
```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRstuVWXyz
ADMINS=123456789
CHANNELS=
```
- `BOT_TOKEN`: [@BotFather](https://t.me/BotFather) dan olingan bot tokeni.
- `ADMINS`: O'zingizning Telegram ID raqamingiz ([@userinfobot](https://t.me/userinfobot) orqali bilib olishingiz mumkin).
- `CHANNELS`: (Ixtiyoriy) Majburiy a'zo bo'linishi kerak bo'lgan kanal username lari (masalan: `@kitobist_uz`).

### 2. Botni ishga tushirish

Loyihada virtual muhit (`venv`) va kutubxonalar allaqachon o'rnatilgan:

```powershell
.\venv\Scripts\python bot.py
```

---

## 📁 Loyiha Tuzilishi

```
Kitobist/
├── assets/
│   └── banner.jpg          # Tanlov uchun tayyorlangan nafis banner rasmi
├── database/
│   ├── __init__.py
│   └── db.py               # Asinxron SQLite (aiosqlite) ma'lumotlar bazasi
├── handlers/
│   ├── __init__.py
│   ├── user.py             # Foydalanuvchi bo'limlari (start, referal, menyular)
│   └── admin.py            # Admin panel va rassilka tizimi
├── keyboards/
│   ├── __init__.py
│   ├── default.py          # Reply menyu tugmalari
│   └── inline.py           # Inline va ulashish tugmalari
├── utils/
│   ├── __init__.py
│   └── subscription.py     # Kanal obunalarini tekshirish
├── .env                    # Sozlamalar va tokenlar
├── bot.py                  # Asosiy ishga tushirish fayli
└── requirements.txt        # Kerakli Python kutubxonalari
```
