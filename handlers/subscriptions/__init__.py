from aiogram import Router

from handlers.subscriptions import _subscribe, _unsubscribe

router = Router(name="Subscriptions")

router.include_routers(_subscribe.router, _unsubscribe.router)
