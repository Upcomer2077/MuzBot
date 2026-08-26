from aiogram.types import BotCommand

COMMANDS = [
    BotCommand(command="start", description="🚀 Запустить бота"),
    BotCommand(command="help", description="❓ Инструкция по использованию"),
    BotCommand(
        command="force",
        description="⚡ Скачать трек напрямую по ссылке из youtube.music.com",
    ),
    BotCommand(command="plist", description="⚡ Скачать плейлист по ссылке"),
]
