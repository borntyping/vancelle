import importlib.metadata
import json
import textwrap

import flask
import sentry_sdk
import structlog

from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import fragment, nothing, script

logger = structlog.get_logger(logger_name=__name__)


class SentryExtension:
    CORS_ALLOW_HEADERS = ["sentry-trace", "baggage"]
    CORS_EXPOSE_HEADERS = ["sentry-trace", "baggage"]

    def init_app(self, app: flask.Flask) -> None:
        app.config.setdefault("SENTRY_ENABLED", True)
        app.config.setdefault("SPOTLIGHT_ENABLED", True)

        if not self.sentry_enabled(app):
            return

        sentry_sdk.init(
            enable_tracing=True,
            in_app_include=["vancelle"],
            release=self.release(),
            send_default_pii=True,
            spotlight=True,
            trace_propagation_targets=[],
            traces_sampler=self.traces_sampler,
            integrations=[],
        )

        app.before_request(self.before_request)

    def sentry_enabled(self, app=flask.current_app) -> bool:
        return app.debug and app.config["SENTRY_ENABLED"]

    def spotlight_enabled(self, app=flask.current_app) -> bool:
        return app.debug and app.config["SPOTLIGHT_ENABLED"]

    @staticmethod
    def release() -> str:
        """https://docs.sentry.io/platforms/python/configuration/releases/"""
        return "vancelle@{}".format(importlib.metadata.version("vancelle"))

    @staticmethod
    def before_request():
        """https://docs.sentry.io/platforms/python/usage/distributed-tracing/custom-instrumentation/"""
        sentry_sdk.continue_trace(flask.request.headers)

    @staticmethod
    def traces_sampler(sampling_context) -> float:
        """https://docs.sentry.io/platforms/python/configuration/sampling/"""
        path_info = sampling_context["wsgi_environ"]["PATH_INFO"]

        if path_info.startswith("/_debug_toolbar"):
            return 0.0

        if path_info.startswith("/static"):
            return 0.0

        return 1.0

    def spotlight_script(self) -> Heavymetal:
        if not self.spotlight_enabled():
            return nothing()

        importmap = {
            "imports": {
                "sentry-spotlight": flask.url_for("static", filename="dist/sentry/sentry-spotlight.js"),
            }
        }
        content = textwrap.dedent(
            """
            import * as Spotlight from 'sentry-spotlight';
            Spotlight.init({ openOnInit: false });
            """
        )

        return fragment(
            [
                script({"type": "importmap"}, json.dumps(importmap)),
                script({"type": "module"}, content),
            ]
        )
