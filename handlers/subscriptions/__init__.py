from aiogram import Router

from handlers.subscriptions import _list, _subscribe, _unsubscribe

router = Router(name="Subscriptions")

router.include_routers(*[x.router for x in [_subscribe, _unsubscribe, _list]])
