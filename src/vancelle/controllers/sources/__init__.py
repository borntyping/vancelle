from .base import Source as Source
from .goodreads import GoodreadsPublicBookSource
from .openlibrary import OpenlibraryEditionSource, OpenlibraryWorkSource
from .royalroad import RoyalroadFictionSource
from .steam import SteamApplicationSource
from .tmdb import TmdbMovieSource, TmdbTvSeriesSource
from .goodreads import GoodreadsPrivateBookSource
from .imported import ImportedWorkSource

EXTERNAL_SOURCES = (
    GoodreadsPublicBookSource(),
    OpenlibraryWorkSource(),
    OpenlibraryEditionSource(),
    RoyalroadFictionSource(),
    SteamApplicationSource(),
    TmdbMovieSource(),
    TmdbTvSeriesSource(),
)

INTERNAL_SOURCES = (
    GoodreadsPrivateBookSource(),
    ImportedWorkSource(),
)
