from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config import ADMINS
from database import db
from utils.subscription import check_user_subscriptions
from keyboards import channels_check_keyboard

class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        # Adminlar uchun majburiy obuna cheklovi yo'q
        if user.id in ADMINS:
            return await handler(event, data)

        # Callback query check_subscription bo'lsa o'tkazib yuboramiz (tekshirish uchun)
        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            return await handler(event, data)

        bot = data.get("bot")
        channels = await db.get_channels()
        if not channels:
            return await handler(event, data)

        is_sub, unsubscribed = await check_user_subscriptions(bot, user.id, channels)
        if not is_sub:
            text = "⚠️ <b>Botdan to'liq foydalanish uchun quyidagi kanallarga a'zo bo'ling:</b>"
            reply_markup = channels_check_keyboard(unsubscribed)
            
            if isinstance(event, Message):
                await event.answer(text, reply_markup=reply_markup, parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ Avval barcha kanallarga a'zo bo'ling!", show_alert=True)
                try:
                    await event.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
                except Exception:
                    pass
            return  # Davom etishni to'xtatish!

        return await handler(event, data)
