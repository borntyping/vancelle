import json
import typing

import flask
import markupsafe

from vancelle.controllers.source import SourceController
from vancelle.extensions import htmx, sentry
from vancelle.html.vancelle.components.footer import PageFooter
from vancelle.html.vancelle.components.navbar import PageNavbar
from vancelle.html.vancelle.components.title import page_title
from vancelle.html.vancelle.components.toast import ToastAside
from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent
from vancelle.lib.heavymetal.html import html5, link, main, meta, script


source_controller = SourceController()


def static(filename: str) -> str:
    return flask.url_for("static", filename=filename)


def Page(
    content: HeavymetalContent,
    *,
    before: HeavymetalContent = (),
    after: HeavymetalContent = (),
    fluid: bool = False,
    title: typing.Sequence[str] = (),
) -> Heavymetal:
    head = [
        page_title(*title),
        meta({"name": "viewport", "content": "width=device-width, initial-scale=1"}),
        meta({"name": "apple-mobile-web-app-title", "content": "Vancelle"}),
        meta({"name": "application-name", "content": "Vancelle"}),
        meta({"name": "msapplication-TileColor", "content": "#485fc7"}),
        meta({"name": "msapplication-config", "content": static("browserconfig.xml")}),
        meta({"name": "theme-color", "content": "#485fc7"}),
        meta({"name": "htmx-config", "content": json.dumps({"globalViewTransitions": True, "requestClass": "is-loading"})}),
        link({"rel": "stylesheet", "href": static("dist/style.css")}),
        link({"rel": "stylesheet", "href": static("dist/bootstrap-icons/font/bootstrap-icons.min.css")}),
        link({"rel": "apple-touch-icon", "href": static("favicon/apple-touch-icon.png"), "sizes": "180x180"}),
        link({"rel": "icon", "href": static("favicon/favicon-32x32.png"), "type": "image/png", "sizes": "32x32"}),
        link({"rel": "icon", "href": static("favicon/favicon-194x194.png"), "type": "image/png", "sizes": "194x194"}),
        link({"rel": "icon", "href": static("favicon/android-chrome-192x192.png"), "type": "image/png", "sizes": "192x192"}),
        link({"rel": "icon", "href": static("favicon/favicon-16x16.png"), "type": "image/png", "sizes": "16x16"}),
        link({"rel": "mask-icon", "href": static("favicon/safari-pinned-tab.svg"), "color": "#485fc7"}),
        link({"rel": "shortcut icon", "href": static("favicon/favicon.ico")}),
        link({"rel": "manifest", "href": static("manifest.json")}),
    ]

    body = [
        PageNavbar(),
        *before,
        main({"class": "container-fluid my-5" if fluid else "container my-5"}, content),
        *after,
        ToastAside(),
        PageFooter(),
        script({"src": static("dist/htmx.org/htmx.min.js")}),
        script({"src": static("dist/htmx-ext-loading-states/loading-states.js")}),
        script({"src": static("dist/hyperscript.org/_hyperscript.min.js")}),
        script({"src": static("dist/bootstrap/bootstrap.bundle.min.js")}),
        script({"src": static("script.js")}),
        sentry.spotlight_script(),
    ]

    return html5(
        {"class": "bg-body-tertiary"},
        [
            ("head", {}, head),
            (
                "body",
                {
                    "class": "bg-body",
                    "hx-ext": "loading-states",
                    "hx-headers": markupsafe.Markup(json.dumps(htmx.headers())),
                },
                body,
            ),
        ],
    )
