from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from handlers._lang.callbacks import SwitchLangCallback
from localization import L10N

router = Router()


@router.message(Command("lang", "language"))
async def cmd_language(message: Message, i18n: I18nContext):
    await message.answer(
        text=i18n.get(L10N["lang"].lang_select_text),
        reply_markup=InlineKeyboardBuilder()
        .button(text="Русский", callback_data=SwitchLangCallback(lang="ru"))
        .button(text="English", callback_data=SwitchLangCallback(lang="en"))
        .as_markup(),
    )


@router.callback_query(SwitchLangCallback.filter())
async def process_change_lang(
    callback: CallbackQuery,
    i18n: I18nContext,
    callback_data: SwitchLangCallback,
):
    new_locale = callback_data.lang

    await i18n.set_locale(new_locale)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            text=i18n.get(L10N["lang"].lang_changed),
            reply_markup=None,
        )
    await callback.answer()
