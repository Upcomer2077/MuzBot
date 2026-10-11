from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

from localization import L10N

router = Router()


def get_lang_keyboard():

    return (
        InlineKeyboardBuilder()
        .button(text="Русский 🇷🇺", callback_data="set_lang:ru")
        .button(text="English 🇬🇧", callback_data="set_lang:en")
    ).as_markup()


@router.message(Command("lang", "language"))
async def cmd_language(message: Message, i18n: I18nContext):
    await message.answer(
        text=i18n.get(L10N["lang"].lang_select_text), reply_markup=get_lang_keyboard()
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def process_change_lang(callback: CallbackQuery, i18n: I18nContext):
    # Достаем выбранную локаль из callback_query_data (ru или en)
    new_locale = callback.data.split(":")[1]

    await i18n.set_locale(new_locale)

    # Отвечаем пользователю. Текст i18n.lang_changed() автоматически
    # возьмется уже из НОВОГО выбранного языка!
    await callback.message.edit_text(
        text=i18n.get(L10N["lang"].lang_changed),
        reply_markup=None,  # Убираем кнопки после выбора
    )
    await callback.answer()
