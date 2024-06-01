from vancelle.html.helpers import HtmlClasses, html_classes
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import button, div, fragment, section, span, strong

TOAST_CONTAINER_ID = "v-notifications"


def toast(title: str, body: str, *, classes: HtmlClasses = ()) -> Heavymetal:
    return div(
        {"class": html_classes("toast show", classes)},
        [
            div(
                {"class": "toast-header"},
                [
                    strong({"class": "me-auto"}, [title]),
                    button({"class": "btn-close", "type": "button", "data-bs-dismiss": "toast"}, []),
                ],
            ),
            div({"class": "toast-body"}, [body]),
        ],
    )


def toast_response(title: str, body: str, *, classes: HtmlClasses = ()) -> Heavymetal:
    return fragment(
        [
            span({}, [title, ": ", body]),
            section(
                {"id": TOAST_CONTAINER_ID, "hx-swap-oob": "beforeend"},
                [toast(title, body, classes=classes)],
            ),
        ]
    )


def toast_container() -> Heavymetal:
    return section(
        {
            "id": TOAST_CONTAINER_ID,
            "class": "toast-container position-absolute bottom-0 start-0 p-3",
            "style": "z-index: 11;",
        },
        [],
    )
