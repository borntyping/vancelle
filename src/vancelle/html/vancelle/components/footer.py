import flask

from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, div, footer, img


def toggle_theme() -> Heavymetal:
    return ("a", {"href": "", "data-theme-toggle": True}, ["Toggle light/dark mode."])


def created_by() -> Heavymetal:
    author = a({"href": "https://borntyping.co.uk"}, "@borntyping")
    return ("span", {}, ["Created by ", author, ". "])


def source_code() -> Heavymetal:
    source = a({"href": "https://github.com/borntyping/vancelle"}, "github.com/borntyping/vancelle")
    return ("span", {}, ["Source code at ", source, "."])


def tmdb_notice() -> Heavymetal:
    """TMDB terms of use require this notice: https://developer.themoviedb.org/docs/faq"""
    return ("span", {}, ["This product uses the TMDB API but is not endorsed or certified by TMDB."])


def dependency_logo(name: str, *, id: str, href: str, src: str) -> Heavymetal:
    return a({"href": href, "id": id, "title": name}, [img({"src": src, "alt": name, "style": "height: 2em !important"})])


def openlibrary() -> Heavymetal:
    return a(
        {"id": "openlibrary", "href": "https://openlibrary.org", "title": "Open Library"},
        [
            img(
                {
                    "height": "24",
                    "src": flask.url_for("static", filename="img/openlibrary.svg"),
                    "alt": "Open Library",
                }
            )
        ],
    )


def tmdb() -> Heavymetal:
    return a(
        {"id": "tmdb", "href": "https://www.themoviedb.org", "title": "The Movie Database"},
        [
            img(
                {
                    "height": "24",
                    "src": flask.url_for("static", filename="img/tmdb.svg"),
                    "alt": "The Movie Database",
                }
            )
        ],
    )


def steam() -> Heavymetal:
    return a(
        {"id": "steam", "href": "https://store.steampowered.com", "title": "Steam"},
        [
            img({"height": "24", "src": flask.url_for("static", filename="img/steam.svg"), "alt": "Steam"}),
        ],
    )


def page_footer() -> Heavymetal:
    """
    Open Library requests a "courtesy link". https://openlibrary.org/dev/docs/api/covers
    TMDB terms of use require a notice: https://developer.themoviedb.org/docs/faq
    """

    return footer(
        {"id": "x-footer", "class": "bg-body-tertiary py-5 mt-5 text-body-secondary"},
        [
            div(
                {"class": "container"},
                [
                    row(
                        {},
                        [
                            col(
                                {"class": "row row-cols-1 align-items-center text-start"},
                                [
                                    div({"class": "col text-right"}, [openlibrary()]),
                                    div({"class": "col text-right"}, [tmdb()]),
                                    div({"class": "col text-right"}, [steam()]),
                                ],
                            ),
                            col(
                                {"class": "row row-cols-1 align-items-center text-end"},
                                [
                                    ("p", {}, [created_by()]),
                                    ("p", {}, [source_code()]),
                                    ("p", {}, [toggle_theme()]),
                                    ("small", {}, [tmdb_notice()]),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ],
    )
