from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from middlewares.handle_errors import BlockedLogMiddleware

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.errors.outer_middleware(BlockedLogMiddleware())
