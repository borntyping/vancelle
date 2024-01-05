import logging
import os
import pathlib

import flask
import pytest
import structlog

from vancelle.app import create_app


@pytest.fixture()
def app() -> flask.Flask:
    return create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "STEAM_WEB_API_KEY": "",
            "TMDB_READ_ACCESS_TOKEN": "invalid",
        }
    )


@pytest.fixture()
def root() -> pathlib.Path:
    return pathlib.Path(__file__).parent


@pytest.fixture()
def fixtures(root: pathlib.Path) -> pathlib.Path:
    return root / "fixtures"


if "TEAMCITY_VERSION" in os.environ:

    @pytest.fixture(scope="session", autouse=True)
    def fix_logging() -> None:
        structlog.configure_once(wrapper_class=structlog.make_filtering_bound_logger(logging.ERROR))
