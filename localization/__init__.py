from typing import Final, TypedDict

from localization.blocks.albums import _AlbumsBlock
from localization.blocks.cancel import _CancelBlock
from localization.blocks.catalog import _CatalogBlock
from localization.blocks.help import _HelpBlock
from localization.blocks.lang import _LanguageBlock
from localization.blocks.playlist import _PlaylistBlock
from localization.blocks.recommendations import _RecommendationsBlock
from localization.blocks.search import _SearchBlock
from localization.blocks.shared import _SharedBlock
from localization.blocks.singles import _SingleBlock
from localization.blocks.start import _StartBlock
from localization.blocks.subscriptions import _SubscriptionsBlock


class _LocalizationStruct(TypedDict):
    start: _StartBlock
    help: _HelpBlock
    cancel: _CancelBlock
    shared: _SharedBlock
    lang: _LanguageBlock
    subs: _SubscriptionsBlock
    single: _SingleBlock
    search: _SearchBlock
    recommendations: _RecommendationsBlock
    playlist: _PlaylistBlock
    catalog: _CatalogBlock
    albums: _AlbumsBlock


L10N: Final[_LocalizationStruct] = {
    "start": _StartBlock(),
    "help": _HelpBlock(),
    "cancel": _CancelBlock(),
    "shared": _SharedBlock(),
    "lang": _LanguageBlock(),
    "subs": _SubscriptionsBlock(),
    "single": _SingleBlock(),
    "search": _SearchBlock(),
    "recommendations": _RecommendationsBlock(),
    "playlist": _PlaylistBlock(),
    "catalog": _CatalogBlock(),
    "albums": _AlbumsBlock(),
}
