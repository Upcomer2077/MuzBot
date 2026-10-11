from aiogram.filters.callback_data import CallbackData


class SwitchLangCallback(CallbackData, prefix="set_lang"):
    lang: str
