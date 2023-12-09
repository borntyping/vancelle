import flask
import importlib.metadata


class SentryExtension:
    def init_app(self, app: flask.Flask) -> None:
        app.config.setdefault("SENTRY_ENABLED", False)
        app.jinja_env.globals["sentry"] = self

        if self._app_is_enabled(app):
            import sentry_sdk

            sentry_sdk.init(release=self.release(), spotlight=True, enable_tracing=True)

    def enabled(self) -> bool:
        return self._app_is_enabled(flask.current_app)

    def _app_is_enabled(self, app: flask.Flask) -> bool:
        return app.debug and app.config["SENTRY_ENABLED"]

    @staticmethod
    def release() -> str:
        return "vancelle@{}".format(importlib.metadata.version("vancelle"))
