from aiogram.types import BotCommandScopeDefault

from _logger import LOGGER
from bot.bot import bot
from bot.commands import COMMANDS
from bot.dispatcher import TGDispatcher
from bot.i18n import i18n
from handlers import get_handlers_router


async def main():
    bot_dispatcher = TGDispatcher(logger=LOGGER)
    dp = bot_dispatcher.get_dispatcher()
    dp.include_router(get_handlers_router())
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        commands=[k["frontend"] for k in COMMANDS.values()],
        scope=BotCommandScopeDefault(),
    )
    i18n.setup(dispatcher=dp)

    await dp.start_polling(bot)
