import dataclasses

import flask
import sentry_sdk
import werkzeug.wrappers.response


@dataclasses.dataclass()
class HtmxExtension:
    """
    https://htmx.org/reference/#request_headers
    """

    CORS_ALLOW_HEADERS = [
        "HX-Boosted",
        "HX-Current-URL",
        "HX-History-Restore-Request",
        "HX-Prompt",
        "HX-Request",
        "HX-Target",
        "HX-Trigger-Name",
        "HX-Trigger",
    ]
    CORS_EXPOSE_HEADERS = [
        "HX-Location",
        "HX-Push-Url",
        "HX-Redirect",
        "HX-Refresh",
        "HX-Replace-Url",
        "HX-Reswap",
        "HX-Retarget",
        "HX-Reselect",
        "HX-Trigger",
        "HX-Trigger-After-Settle",
        "HX-Trigger-After-Swap",
    ]

    def __init__(self, app: flask.Flask | None = None) -> None:
        if app:
            self.init_app(app)

    def init_app(self, app: flask.Flask):
        app.jinja_env.globals["htmx"] = self

    def __bool__(self):
        return self.hx_request and not self.hx_boosted

    @property
    def hx_boosted(self) -> bool:
        return flask.request.headers.get("HX-Boosted") == "true"

    @property
    def hx_request(self) -> bool:
        return flask.request.headers.get("HX-Request") == "true"

    @property
    def hx_target(self) -> str | None:
        return flask.request.headers.get("HX-Target")

    @property
    def hx_trigger(self) -> str | None:
        return flask.request.headers.get("HX-Trigger")

    @property
    def hx_trigger_name(self) -> str | None:
        return flask.request.headers.get("HX-Trigger-Name")

    def refresh(self) -> flask.Response | werkzeug.wrappers.response.Response:
        """
        Refresh the page that initiated the request, either via
        HX-Refresh or redirecting to the request's Referer.
        """
        if not self.hx_request:
            return flask.redirect(flask.request.referrer)

        return flask.Response(status=204, headers={"HX-Refresh": "true"})

    def redirect(self, url: str) -> flask.Response | werkzeug.wrappers.response.Response:
        """
        Redirect to a page via HX-Redirect or a normal Location header.
        """
        if not self.hx_request:
            return flask.redirect(url)

        return flask.Response(status=204, headers={"HX-Redirect": url})

    def headers(self) -> dict[str, str]:
        return {
            "sentry-trace": sentry_sdk.get_traceparent(),
            "baggage": sentry_sdk.get_baggage(),
        }
