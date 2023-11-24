import typing

import flask

from vancelle.controllers.sources.base import Manager, R
from vancelle.ext.flask_sqlalchemy import Pagination, ItemsPagination
from vancelle.extensions import apis, p
from vancelle.models import TmdbMovie, TmdbTvSeries, Work


class TmdbMovieManager(Manager[TmdbMovie]):
    remote_type = TmdbMovie

    def fetch(self, remote_id: str) -> TmdbMovie:
        data = apis.tmdb.movie(remote_id)
        return TmdbMovie(
            id=str(data["id"]),
            title=data["title"],
            author=p.join([c["name"] for c in data["production_companies"]]),
            description=data["overview"],
            release_date=apis.tmdb.release_date(data["release_date"]),
            cover=apis.tmdb.poster_url(data["poster_path"]),
            background=apis.tmdb.backdrop_url(data["backdrop_path"]),
            data=data,
        )

    def search(self, query: str) -> ItemsPagination[TmdbMovie]:
        page = flask.request.args.get("page", 1, type=int)
        data = apis.tmdb.search_movies(query, page=page)

        items = [
            TmdbMovie(
                id=result["id"],
                title=result["title"],
                description=result["overview"],
                cover=apis.tmdb.poster_url(result["poster_path"]),
            )
            for result in data["results"]
        ]

        return ItemsPagination(page=page, per_page=20, items=items, total=data["total_results"])


class TmdbTvSeriesManager(Manager[TmdbTvSeries]):
    remote_type = TmdbTvSeries

    def fetch(self, remote_id: str) -> TmdbTvSeries:
        data = apis.tmdb.tv(remote_id)
        return TmdbTvSeries(
            id=str(data["id"]),
            title=data["name"],
            author=p.join([c["name"] for c in data["production_companies"]]),
            description=data["overview"],
            release_date=apis.tmdb.release_date(data["first_air_date"]),
            cover=apis.tmdb.poster_url(data["poster_path"]),
            background=apis.tmdb.backdrop_url(data["backdrop_path"]),
            data=data,
        )

    def search(self, query: str) -> Pagination[TmdbTvSeries]:
        page = flask.request.args.get("page", 1, type=int)
        data = apis.tmdb.search_tv(query, page=page)

        items = [
            TmdbTvSeries(
                id=result["id"],
                title=result["name"],
                description=result["overview"],
                cover=apis.tmdb.poster_url(result["poster_path"]),
            )
            for result in data["results"]
        ]

        return ItemsPagination(page=page, per_page=20, items=items, total=data["total_results"])
