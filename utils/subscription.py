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

def format_channel_id(ch_id: str | int) -> str | int:
    """Kanal ID yoki username ni to'g'ri formatga keltirish"""
    ch_str = str(ch_id).strip()
    # Agar raqamli ID bo'lsa (masalan -100123456789 yoki 123456789)
    if ch_str.startswith("-") and ch_str[1:].isdigit():
        return int(ch_str)
    if ch_str.isdigit():
        return int(f"-100{ch_str}") if not ch_str.startswith("100") else int(f"-{ch_str}")
    # Agar username bo'lsa (@ bilan)
    if not ch_str.startswith("@") and not ch_str.startswith("-"):
        return f"@{ch_str}"
    return ch_str

async def check_user_subscriptions(bot: Bot, user_id: int, channels: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Foydalanuvchining majburiy kanallarga a'zo bo'lganligini tekshirish.
    Qaytaradi: (barchasiga a'zomi: bool, a'zo bo'lmagan kanallar ro'yxati: list)
    """
    if not channels:
        return True, []

    unsubscribed = []
    for ch in channels:
        raw_id = ch["channel_id"]
        chat_identifier = format_channel_id(raw_id)
        try:
            member = await bot.get_chat_member(chat_id=chat_identifier, user_id=user_id)
            if member.status not in ALLOWED_STATUSES:
                unsubscribed.append(ch)
        except Exception as e:
            logger.warning(f"Kanal obunasini tekshirishda xatolik (Kanal: {chat_identifier}, User: {user_id}): {e}")
            err_str = str(e).lower()
            # Agar botning o'zi kanalda admin bo'lmasa yoki kanal topilmasa, oddiy foydalanuvchini butunlay bloklab qo'ymaslik
            if "not a member" in err_str or "chat not found" in err_str or "admin rights" in err_str:
                logger.error(f"⚠️ Bot '{chat_identifier}' kanalida admin emas! Botni kanalda admin qiling.")
                continue
            unsubscribed.append(ch)

    return len(unsubscribed) == 0, unsubscribed
