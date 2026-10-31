from typing import List, Dict, Any, Tuple
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
import logging

logger = logging.getLogger(__name__)

ALLOWED_STATUSES = [
    ChatMemberStatus.CREATOR,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.RESTRICTED
]

async def check_user_subscriptions(bot: Bot, user_id: int, channels: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Foydalanuvchining majburiy kanallarga a'zo bo'lganligini tekshirish.
    Qaytaradi: (barchasiga a'zomi: bool, a'zo bo'lmagan kanallar ro'yxati: list)
    """
    if not channels:
        return True, []

    unsubscribed = []
    for ch in channels:
        ch_id = ch["channel_id"]
        try:
            member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
            if member.status not in ALLOWED_STATUSES:
                unsubscribed.append(ch)
        except Exception as e:
            # Agar bot kanal admini bo'lmasa yoki kanal topilmasa xato bermasligi uchun
            logger.warning(f"Kanal obunasini tekshirishda xatolik ({ch_id}): {e}")
            pass

    return len(unsubscribed) == 0, unsubscribed
