import dataclasses
import datetime
import functools
import typing

import flask
import hishel
import svcs

from vancelle.clients.client import HttpClient, HttpClientBuilder
from vancelle.ext.httpx import BearerAuth


class ConfigurationImages(typing.TypedDict):
    base_url: str
    secure_base_url: str
    backdrop_sizes: list[str]
    logo_sizes: list[str]
    poster_sizes: list[str]
    profile_sizes: list[str]
    still_sizes: list[str]


class Configuration(typing.TypedDict):
    images: ConfigurationImages


class Genre(typing.TypedDict):
    """https://developer.themoviedb.org/reference/movie-details"""

    id: int
    name: str


class ProductionCompany(typing.TypedDict):
    """https://developer.themoviedb.org/reference/movie-details"""

    id: int
    logo_path: str
    name: str
    origin_country: str


class ProductionCountry(typing.TypedDict):
    """https://developer.themoviedb.org/reference/movie-details"""

    iso_3166_1: str
    name: str


class MovieDetails(typing.TypedDict):
    """https://developer.themoviedb.org/reference/movie-details"""

    adult: bool
    backdrop_path: str
    belongs_to_collection: str | None
    budget: int
    genres: list[Genre]
    homepage: str
    id: int
    imdb_id: str
    original_language: str
    original_title: str
    overview: str
    popularity: float
    poster_path: str
    production_companies: list[ProductionCompany]
    production_countries: list[ProductionCountry]
    release_date: str  # 2004-07-23
    revenue: int
    runtime: int
    spoken_languages: list[dict]
    status: str  # 'Released'
    tagline: str
    title: str
    video: bool
    vote_average: float
    vote_count: int


class SearchMovieResult(typing.TypedDict):
    adult: bool
    backdrop_path: str
    id: int
    original_language: str
    original_title: str
    overview: str
    popularity: float
    poster_path: str
    release_date: str  # 2004-07-23
    title: str
    video: bool
    vote_average: float
    vote_count: int


class SearchMovieResults(typing.TypedDict):
    page: int
    results: typing.Sequence[SearchMovieResult]
    total_pages: int
    total_results: int


class TvDetails(typing.TypedDict):
    """https://developer.themoviedb.org/reference/tv-series-details"""

    adult: bool
    backdrop_path: str
    created_by: dict
    episode_run_time: list
    first_air_date: str
    genres: list[Genre]
    homepage: str
    id: int
    in_production: bool
    languages: list[str]
    last_air_date: str
    last_episode_to_air: dict
    name: str
    next_episode_to_air: dict
    networks: list[dict]
    number_of_episodes: int
    number_of_seasons: int
    origin_country: list[str]
    original_name: str
    overview: str
    popularity: float
    poster_path: str
    production_companies: list[ProductionCompany]
    production_countries: list[ProductionCountry]
    seasons: list[dict]
    spoken_languages: list[dict]
    status: str
    tagline: str
    type: str
    vote_average: float
    vote_count: int


class SearchTvResult(typing.TypedDict):
    """https://developer.themoviedb.org/reference/search-tv"""

    adult: bool
    backdrop_path: str
    id: int
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: str
    first_air_date: str  # 2004-07-23
    name: str
    video: bool
    vote_average: float
    vote_count: int


class SearchTvResults(typing.TypedDict):
    """https://developer.themoviedb.org/reference/search-tv"""

    page: int
    results: typing.Sequence[SearchTvResult]
    total_pages: int
    total_results: int


@dataclasses.dataclass()
class TmdbAPI(HttpClient):
    client: hishel.CacheClient

    @classmethod
    def factory(cls, svcs_container: svcs.Container) -> typing.Self:
        app, builder = svcs_container.get(flask.Flask, HttpClientBuilder)
        return cls(
            client=hishel.CacheClient(
                storage=builder.sqlite_storage_for(cls),
                auth=BearerAuth(app.config["TMDB_READ_ACCESS_TOKEN"]),
            ),
        )

    @functools.cached_property
    def configuration(self) -> Configuration:
        response = self.get(
            "https://api.themoviedb.org/3/configuration",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    def search_movies(self, query: str, page: int) -> SearchMovieResults:
        """https://developer.themoviedb.org/reference/search-movie"""
        response = self.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"query": query, "include_adult": "false", "language": "en-GB", "page": str(page)},
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    def movie(self, movie_id: str) -> MovieDetails:
        """https://developer.themoviedb.org/reference/movie-details"""
        response = self.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    def search_tv(self, query: str, page: int) -> SearchTvResults:
        """https://developer.themoviedb.org/reference/search-tv"""
        response = self.get(
            "https://api.themoviedb.org/3/search/tv",
            params={"query": query, "include_adult": "false", "language": "en-GB", "page": str(page)},
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    def tv(self, tv_id: str) -> TvDetails:
        """https://developer.themoviedb.org/reference/tv-series-details"""
        response = self.get(
            f"https://api.themoviedb.org/3/tv/{tv_id}",
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    def backdrop_url(self, file_path, file_size: str = "w780") -> str | None:
        """Sizes at time of writing: ["w300", "w780", "w1280", "original"]."""
        return self.build_image_url(file_path, file_size)

    def poster_url(self, file_path, file_size: str = "w342") -> str | None:
        """Sizes at time of writing: ["w92", "w154", "w185", "w342", "w500", "w780", "original"]."""
        return self.build_image_url(file_path, file_size)

    def build_image_url(self, file_path: str, file_size: str) -> str | None:
        """
        https://developer.themoviedb.org/docs/image-basics
        """
        if file_path is None:
            return None

        base_url = self.configuration["images"]["base_url"]
        return base_url + file_size + file_path

    def release_date(self, release_date: str) -> datetime.date | None:
        if not release_date:
            return None

        return datetime.datetime.strptime(release_date, "%Y-%m-%d").date()
