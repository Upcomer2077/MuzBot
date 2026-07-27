from aiogram.enums import ChatAction

from bot import bot


async def send_action(chat_id: int, action: ChatAction = ChatAction.UPLOAD_DOCUMENT):
    """Asynchronously send a specific chat status action to a Telegram user.

    Args:
        chat_id: Unique identifier for the target Telegram chat.
        action: The type of Telegram ChatAction activity to display. Defaults to ChatAction.UPLOAD_DOCUMENT.
    """
    await bot.send_chat_action(
        chat_id=chat_id,
        action=action,
    )
