import typing

import flask


def url_with(endpoint: str | None = None, **kwargs):
    """Like url_for(), but keeps parameters from the current request."""
    endpoint = endpoint if endpoint else flask.request.endpoint
    values = flask.request.view_args | flask.request.args | kwargs  # type: ignore

    assert endpoint is not None
    return flask.url_for(endpoint=endpoint, **values)


def compare_endpoints(*, request_endpoint: str, request_args: dict, other_endpoint: str, other_args: dict) -> bool:
    """Testable implementation of 'url_is_active()'."""
    return request_endpoint == other_endpoint and all(request_args.get(k) == v for k, v in other_args.items())


def url_is_active(endpoint: str, **kwargs: typing.Any) -> bool:
    """
    Compare an endpoint and it's arguments to the current request, returning true if they match.

    `/works/?work_type='books'&work_shelf='upcoming'` should match `url_is_active('works.index', work_type='books')`.
    """
    return compare_endpoints(
        request_endpoint=flask.request.endpoint,
        request_args=(flask.request.view_args or {}) | flask.request.args,
        other_endpoint=endpoint,
        other_args=kwargs,
    )
