from aiogram_i18n.cores import FluentCompileCore
from aiogram_i18n.managers import FSMManager
from aiogram_i18n.middleware import I18nMiddleware

i18n = I18nMiddleware(
    core=FluentCompileCore(path="localization/locales/{locale}/"),
    default_locale="en",
    manager=FSMManager(),
)
