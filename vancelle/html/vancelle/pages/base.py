import json

import flask

from vancelle.html.components.title import title
from vancelle.html.document import document, link, meta, script
from vancelle.html.hotmetal import Hotmetal, element
from vancelle.html.vancelle.components.footer import page_footer
from vancelle.html.vancelle.components.navbar import page_navbar


def content_section(*content: Hotmetal) -> Hotmetal:
    return element("main", {"class": "section"}, [("div", {"class": "container block"}, list(content))])


def page(
    *content: Hotmetal,
    before: Hotmetal | None = None,
    after: Hotmetal | None = None,
) -> Hotmetal:
    head = [
        title(),
        meta("viewport", "width=device-width, initial-scale=1"),
        meta("apple-mobile-web-app-title", "Vancelle"),
        meta("application-name", "Vancelle"),
        meta("msapplication-TileColor", "#485fc7"),
        meta("msapplication-config", flask.url_for("static", filename="browserconfig.xml")),
        meta("theme-color", "#485fc7"),
        meta("htmx-config", json.dumps({"globalViewTransitions": True, "requestClass": "is-loading"})),
        link("stylesheet", flask.url_for("static", filename="dist/style.css")),
        link("apple-touch-icon", flask.url_for("static", filename="favicon/apple-touch-icon.png"), sizes="180x180"),
        link("icon", flask.url_for("static", filename="favicon/favicon-32x32.png"), type="image/png", sizes="32x32"),
        link("icon", flask.url_for("static", filename="favicon/favicon-194x194.png"), type="image/png", sizes="194x194"),
        link("icon", flask.url_for("static", filename="favicon/android-chrome-192x192.png"), type="image/png", sizes="192x192"),
        link("icon", flask.url_for("static", filename="favicon/favicon-16x16.png"), type="image/png", sizes="16x16"),
        link("mask-icon", flask.url_for("static", filename="favicon/safari-pinned-tab.svg"), color="#485fc7"),
        link("shortcut icon", flask.url_for("static", filename="favicon/favicon.ico")),
        link("manifest", flask.url_for("static", filename="manifest.json")),
    ]

    body = [
        page_navbar(),
        before,
        content_section(*content),
        after,
        page_footer(),
        script("https://unpkg.com/htmx.org@1.9.11/dist/htmx.js"),
        script("https://unpkg.com/htmx.org@1.9.11/dist/ext/debug.js"),
        script("https://unpkg.com/htmx.org@1.9.11/dist/ext/loading-states.js"),
        script("https://unpkg.com/hyperscript.org@0.9.12"),
        script("https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.esm.js", type="module"),
        script(flask.url_for("static", filename="script.js")),
    ]

    return document(("head", {}, head), ("body", {"hx-ext": "loading-states"}, body))
