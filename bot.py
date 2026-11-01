import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiohttp import web

import config
from database import db
from handlers import user_router, admin_router
from utils import SubscriptionMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def handle_health_check(request):
    """Render port monitoringi uchun health-check"""
    return web.Response(text="Bot is running healthy!")

async def start_web_server():
    """Render $PORT uchun web server"""
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    app.router.add_get("/health", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Health-check web server port {port} da ishga tushdi.")

async def main():
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN topilmadi!")
        return

    # Render uchun web serverni fonda ishga tushirish (port scan muammosi bo'lmasligi uchun)
    if os.environ.get("PORT"):
        try:
            await start_web_server()
        except Exception as e:
            logger.warning(f"Web serverni ishga tushirishda xatolik: {e}")

    # Ma'lumotlar bazasini ishga tushirish
    await db.init()
    logger.info("✅ Ma'lumotlar bazasi tayyor.")

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

    # Routerlarni ulash
    user_router.message.middleware(SubscriptionMiddleware())
    user_router.callback_query.middleware(SubscriptionMiddleware())
    dp.include_router(admin_router)
    dp.include_router(user_router)

    bot_info = await bot.get_me()
    logger.info(f"🚀 Bot muvaffaqiyatli ishga tushdi: @{bot_info.username}")

    try:
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
