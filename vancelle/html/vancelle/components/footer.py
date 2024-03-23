import flask

from vancelle.html.document import a, img, whitespace
from vancelle.html.types import Hotmetal, HotmetalAttributes, Href
from vancelle.html.vancelle.elements.picture import light_dark_img


def toggle_theme(attributes: HotmetalAttributes) -> Hotmetal:
    return ("a", {**attributes, "data-theme-toggle": ""}, [f"Toggle light/dark mode."])


def created_by() -> Hotmetal:
    author = a("@borntyping", href="https://borntyping.co.uk")
    return ("span", {}, ["Created by ", author, ". "])


def source_code() -> Hotmetal:
    source = a("github.com/borntyping/vancelle", href="https://github.com/borntyping/vancelle")
    return ("span", {}, ["Source code at ", source, "."])


def tmdb_notice() -> Hotmetal:
    """TMDB terms of use require this notice: https://developer.themoviedb.org/docs/faq"""
    return ("span", {}, ["This product uses the TMDB API but is not endorsed or certified by TMDB."])


def dependency_logo(name: str, *, id: str, href: Href, src: Href) -> Hotmetal:
    return a(
        img(
            src=src,
            alt=name,
            style="height: 2em !important",
        ),
        id=id,
        href=href,
        title=name,
    )


def page_footer() -> Hotmetal:
    """
    Open Library requests a "courtesy link". https://openlibrary.org/dev/docs/api/covers
    TMDB terms of use require a notice: https://developer.themoviedb.org/docs/faq
    """

    return (
        "footer",
        {"id": "x-footer", "class": "footer"},
        [
            (
                "div",
                {"class": "content has-text-centered"},
                [
                    (
                        "p",
                        {},
                        [
                            created_by(),
                            source_code(),
                        ],
                    ),
                    (
                        "p",
                        {"id": "x-dependency-logos"},
                        [
                            a(
                                light_dark_img(
                                    light="https://bulma.io/assets/images/made-with-bulma.png",
                                    dark="https://bulma.io/assets/images/made-with-bulma--dark.png",
                                    alt="Bulma",
                                    width=124,
                                    height=24,
                                ),
                                id="bulma",
                                href="https://bulma.io",
                                title="Made with Bulma",
                            ),
                            a(
                                img(src=flask.url_for("static", filename="img/openlibrary.svg"), alt="Open Library"),
                                id="openlibrary",
                                href="https://openlibrary.org",
                                title="Open Library",
                            ),
                            a(
                                img(src=flask.url_for("static", filename="img/tmdb.svg"), alt="The Movie Database"),
                                id="tmdb",
                                href="https://www.themoviedb.org",
                                title="The Movie Database",
                            ),
                            a(
                                img(src=flask.url_for("static", filename="img/steam.svg"), alt="Steam"),
                                id="steam",
                                href="https://store.steampowered.com",
                                title="Steam",
                            ),
                        ],
                    ),
                    (
                        "p",
                        {"class": "has-text-grey"},
                        [
                            tmdb_notice(),
                            whitespace(),
                            toggle_theme({"class": "has-text-grey"}),
                        ],
                    ),
                ],
            )
        ],
    )
