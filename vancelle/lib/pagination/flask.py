from __future__ import annotations

import dataclasses

import flask


@dataclasses.dataclass()
class FlaskPaginationArgs:
    page: int = dataclasses.field(
        default_factory=lambda: flask.request.args.get("page", 1, int),
        kw_only=True,
    )
    per_page: int = dataclasses.field(
        default_factory=lambda: flask.request.args.get("per_page", 10, int),
        kw_only=True,
    )
    max_per_page: int = dataclasses.field(
        default_factory=lambda: flask.current_app.config.get("PAGINATION_MAX_PER_PAGE", 100),
        kw_only=True,
    )
