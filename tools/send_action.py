from aiogram.enums import ChatAction

from bot import bot


async def send_action(chat_id: int, action: ChatAction = ChatAction.UPLOAD_DOCUMENT):
    await bot.send_chat_action(
        chat_id=chat_id,
        action=action,
    )
