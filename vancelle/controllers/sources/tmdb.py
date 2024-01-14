import flask

from vancelle.controllers.sources.base import Manager
from vancelle.ext.flask_sqlalchemy import ItemsPagination, Pagination
from vancelle.extensions import apis
from vancelle.inflect import p
from vancelle.models.remote import TmdbMovie, TmdbTvSeries
from vancelle.models.work import Film, Show


class TmdbMovieManager(Manager[TmdbMovie]):
    remote_type = TmdbMovie
    work_type = Film

    def fetch(self, remote_id: str) -> TmdbMovie:
        data = apis.tmdb.movie(remote_id)
        return TmdbMovie(
            id=str(data["id"]),
            title=data["title"],
            author=p.join([c["name"] for c in data["production_companies"]]),
            description=data["overview"],
            release_date=apis.tmdb.release_date(data.get("release_date")),
            cover=apis.tmdb.poster_url(data["poster_path"]),
            background=apis.tmdb.backdrop_url(data["backdrop_path"]),
            data=data,
        )

    def search(self, query: str) -> ItemsPagination[TmdbMovie]:
        page = flask.request.args.get("page", 1, type=int)
        search = apis.tmdb.search_movies(query, page=page)

        items = [
            TmdbMovie(
                id=data["id"],
                title=data["title"],
                description=data["overview"],
                cover=apis.tmdb.poster_url(data["poster_path"]),
                release_date=apis.tmdb.release_date(data.get("release_date")),
            )
            for data in search["results"]
        ]

        return ItemsPagination(page=page, per_page=20, items=items, total=search["total_results"])


class TmdbTvSeriesManager(Manager[TmdbTvSeries]):
    remote_type = TmdbTvSeries
    work_type = Show

    def fetch(self, remote_id: str) -> TmdbTvSeries:
        data = apis.tmdb.tv(remote_id)
        return TmdbTvSeries(
            id=str(data["id"]),
            title=data["name"],
            author=p.join([c["name"] for c in data["production_companies"]]),
            description=data["overview"],
            release_date=apis.tmdb.release_date(data.get("first_air_date")),
            cover=apis.tmdb.poster_url(data["poster_path"]),
            background=apis.tmdb.backdrop_url(data["backdrop_path"]),
            data=data,
        )

    def search(self, query: str) -> Pagination[TmdbTvSeries]:
        page = flask.request.args.get("page", 1, type=int)
        search = apis.tmdb.search_tv(query, page=page)

        items = [
            TmdbTvSeries(
                id=data["id"],
                title=data["name"],
                description=data["overview"],
                cover=apis.tmdb.poster_url(data["poster_path"]),
                release_date=apis.tmdb.release_date(data.get("first_air_date")),
            )
            for data in search["results"]
        ]

        return ItemsPagination(page=page, per_page=20, items=items, total=search["total_results"])
