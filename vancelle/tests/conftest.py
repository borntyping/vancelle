import pathlib

import pytest


@pytest.fixture()
def root() -> pathlib.Path:
    return pathlib.Path(__file__).parent


@pytest.fixture()
def fixtures(root: pathlib.Path) -> pathlib.Path:
    return root / "fixtures"
