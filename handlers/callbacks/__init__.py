from aiogram import Router

from handlers.callbacks import _drop_message, download, subscriptions

router = Router(name="Main cb router")

router.include_routers(subscriptions.router, download.router, _drop_message.router)
