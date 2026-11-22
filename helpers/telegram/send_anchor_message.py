from bot.bot import bot


async def send_anchor_message(chat_id: int):
    """Send a stealth placeholder separator text sequence to serve as a target chat reference point.

    Args:
        chat_id: Target conversation path tracking index block identifier.

    Returns:
        The newly created structural chat marker entry message token wrapper.
    """
    return await bot.send_message(
        chat_id,
        "||\\.||",
        parse_mode="MarkdownV2",
    )
