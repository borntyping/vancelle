import json

import flask

from vancelle.html.vancelle.components.footer import page_footer
from vancelle.html.vancelle.components.navbar import page_navbar
from vancelle.html.vancelle.components.title import page_title
from vancelle.html.vancelle.components.toast import toast_container
from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent
from vancelle.lib.heavymetal.html import html5, link, main, meta, script


def static(filename: str) -> str:
    return flask.url_for("static", filename=filename)


def page(
    content: HeavymetalContent,
    fluid: bool = False,
) -> Heavymetal:
    head = [
        page_title(),
        meta({"name": "viewport", "content": "width=device-width, initial-scale=1"}),
        meta({"name": "apple-mobile-web-app-title", "content": "Vancelle"}),
        meta({"name": "application-name", "content": "Vancelle"}),
        meta({"name": "msapplication-TileColor", "content": "#485fc7"}),
        meta({"name": "msapplication-config", "content": static("browserconfig.xml")}),
        meta({"name": "theme-color", "content": "#485fc7"}),
        meta({"name": "htmx-config", "content": json.dumps({"globalViewTransitions": True, "requestClass": "is-loading"})}),
        link({"rel": "stylesheet", "href": static("dist/style.css")}),
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
        page_navbar(),
        main({"class": "container-fluid my-5" if fluid else "container my-5"}, content),
        toast_container(),
        page_footer(),
        script(
            {
                "src": "https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js",
                "integrity": "sha384-I7E8VVD/ismYTF4hNIPjVp/Zjvgyol6VFvRkX/vR+Vc4jQkC+hVqc2pM8ODewa9r",
                "crossorigin": "anonymous",
            }
        ),
        script(
            {
                "src": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js",
                "integrity": "sha384-0pUGZvbkm6XF6gxjEnlmuGrJXVbNuzT9qBBavbLwCsOGabYfZo0T0to5eqruptLy",
                "crossorigin": "anonymous",
            }
        ),
        script({"src": "https://unpkg.com/htmx.org@1.9.11/dist/htmx.js"}),
        script({"src": "https://unpkg.com/htmx.org@1.9.11/dist/ext/debug.js"}),
        script({"src": "https://unpkg.com/htmx.org@1.9.11/dist/ext/loading-states.js"}),
        script({"src": "https://unpkg.com/hyperscript.org@0.9.12"}),
        script({"src": "https://unpkg.com/ionicons@7.1.0/dist/ionicons/ionicons.esm.js", "type": "module"}),
        script({"src": static("script.js")}),
    ]

    return html5(
        {"class": "bg-body-tertiary"},
        [
            ("head", {}, head),
            ("body", {"class": "bg-body", "hx-ext": "loading-states"}, body),
        ],
    )
