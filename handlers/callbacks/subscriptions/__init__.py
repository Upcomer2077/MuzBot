from aiogram import Router

from handlers.callbacks.subscriptions import _sub_cb, _unsub_cb

router = Router(name="Subscriptions cb")

router.include_routers(_sub_cb.router, _unsub_cb.router)
