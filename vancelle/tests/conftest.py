import logging
import os
import pathlib

import pytest
import structlog


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
