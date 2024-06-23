import svcs

from vancelle.clients.tmdb.client import TmdbAPI
from vancelle.controllers.sources.base import Source
from ...lib.pagination import Pagination
from vancelle.inflect import p
from vancelle.models.remote import TmdbMovie, TmdbTvSeries
from vancelle.models.work import Film, Show
from ...lib.pagination.flask import FlaskPaginationArgs


class TmdbMovieSource(Source[TmdbMovie]):
    remote_type = TmdbMovie
    work_type = Film

    def fetch(self, remote_id: str) -> TmdbMovie:
        client = svcs.flask.get(TmdbAPI)
        data = client.movie(remote_id)
        return TmdbMovie(
            id=str(data["id"]),
            title=data["title"],
            author=p.join([c["name"] for c in data["production_companies"]]),
            description=data["overview"],
            release_date=client.release_date(data.get("release_date")),
            cover=client.poster_url(data["poster_path"]),
            background=client.backdrop_url(data["backdrop_path"]),
            data=data,
        )

    def search(self, query: str) -> Pagination[TmdbMovie]:
        args = FlaskPaginationArgs(per_page=20, max_per_page=20)

        client = svcs.flask.get(TmdbAPI)
        search = client.search_movies(query, page=args.page)

        items = [
            TmdbMovie(
                id=str(data["id"]),
                title=data["title"],
                description=data["overview"],
                cover=client.poster_url(data["poster_path"]),
                release_date=client.release_date(data.get("release_date")),
            )
            for data in search["results"]
        ]

        return Pagination(items=items, count=search["total_results"], page=args.page, per_page=args.per_page)


class TmdbTvSeriesSource(Source[TmdbTvSeries]):
    remote_type = TmdbTvSeries
    work_type = Show

    def fetch(self, remote_id: str) -> TmdbTvSeries:
        client = svcs.flask.get(TmdbAPI)
        data = client.tv(remote_id)
        return TmdbTvSeries(
            id=str(data["id"]),
            title=data["name"],
            author=p.join([c["name"] for c in data["production_companies"]]),
            description=data["overview"],
            release_date=client.release_date(data.get("first_air_date")),
            cover=client.poster_url(data["poster_path"]),
            background=client.backdrop_url(data["backdrop_path"]),
            data=data,
        )

    def search(self, query: str) -> Pagination[TmdbTvSeries]:
        args = FlaskPaginationArgs(per_page=20, max_per_page=20)

        client = svcs.flask.get(TmdbAPI)
        search = client.search_tv(query, page=args.page)

        items = [
            TmdbTvSeries(
                id=str(data["id"]),
                title=data["name"],
                description=data["overview"],
                cover=client.poster_url(data["poster_path"]),
                release_date=client.release_date(data.get("first_air_date")),
            )
            for data in search["results"]
        ]

        return Pagination(items=items, count=search["total_results"], page=args.page, per_page=args.per_page)
