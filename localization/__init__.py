from typing import Final, TypedDict

from localization.blocks.L_albums import _AlbumsBlock
from localization.blocks.L_cancel import _CancelBlock
from localization.blocks.L_catalog import _CatalogBlock
from localization.blocks.L_help import _HelpBlock
from localization.blocks.L_lang import _LanguageBlock
from localization.blocks.L_playlist import _PlaylistBlock
from localization.blocks.L_recommendations import _RecommendationsBlock
from localization.blocks.L_search import _SearchBlock
from localization.blocks.L_shared import _SharedBlock
from localization.blocks.L_singles import _SingleBlock
from localization.blocks.L_start import _StartBlock
from localization.blocks.L_subscriptions import _SubscriptionsBlock


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
