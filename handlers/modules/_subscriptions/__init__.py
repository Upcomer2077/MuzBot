from aiogram import Router

from handlers.modules._subscriptions import _list, _sub, _unsub

router = Router(name="Subscriptions")

router.include_routers(*[x.router for x in [_list, _unsub, _sub]])
