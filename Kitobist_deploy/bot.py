import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import config
from database import db
from handlers import user_router, admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def main():
    if not config.BOT_TOKEN:
        logger.error(
            "❌ BOT_TOKEN topilmadi! Iltimos, .env fayliga @BotFather dan olingan bot tokeningizni kiriting."
        )
        print("\n" + "="*50)
        print("DIQQAT: .env faylida BOT_TOKEN ko'rsatilmagan!")
        print("Iltimos, Kitobist/.env faylini oching va BOT_TOKEN ni kiriting.")
        print("="*50 + "\n")
        return

    # Ma'lumotlar bazasini ishga tushirish
    await db.init()
    logger.info("✅ Ma'lumotlar bazasi tayyor.")

    # Agar .env da dastlabki kanallar berilgan bo'lsa, ularni tekshirib kiritish
    if config.CHANNELS:
        for ch in config.CHANNELS:
            clean_ch = ch.strip()
            if clean_ch:
                await db.add_channel(
                    channel_id=clean_ch,
                    channel_title=f"Kanal {clean_ch}",
                    channel_url=f"https://t.me/{clean_ch.lstrip('@')}"
                )

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Routerlarni ulash (Admin birinchi navbatda)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    bot_info = await bot.get_me()
    logger.info(f"🚀 Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")
    print(f"\n>>> Kitobist Boti ishga tushdi: @{bot_info.username} <<<\n")

    try:
        # Eski keshdagi yangilanishlarni tashlab yuborish
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot dasturi yakunlandi.")
