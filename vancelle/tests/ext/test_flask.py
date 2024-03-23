import pytest

from vancelle.ext.flask import compare_endpoints


@pytest.mark.parametrize(
    ("request_endpoint", "request_args", "other_endpoint", "other_args", "result"),
    [
        ("work.index", {"work_type": "book"}, "work.index", {"work_type": "book"}, True),
        ("work.index", {"work_type": "book"}, "work.index", {"work_type": "game"}, False),
    ],
)
def test_compare_endpoints(
    request_endpoint: str,
    request_args: dict,
    other_endpoint: str,
    other_args: dict,
    result: bool,
):
    assert (
        compare_endpoints(
            request_endpoint=request_endpoint,
            request_args=request_args,
            other_endpoint=other_endpoint,
            other_args=other_args,
        )
        == result
    )
