import typing

import flask

from vancelle.controllers.sources.base import Source
from vancelle.forms.source import SourceSearchArgs
from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.vancelle.components.index import SearchFormControls
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, div, form
from vancelle.models import Work


def SourceListGroup(sources: typing.Sequence[Source], *, candidate_work: typing.Optional[Work]) -> Heavymetal:
    return div(
        {"class": "list-group"},
        [
            a(
                {
                    "class": "list-group-item list-group-item-action",
                    "href": flask.url_for(
                        "source.search",
                        remote_type=source.remote_type.polymorphic_identity(),
                        candidate_work=candidate_work,
                    ),
                },
                ["Search ", source.name],
            )
            for source in sources
        ],
    )


def SourceSearchForm(args: SourceSearchArgs, placeholder: str) -> Heavymetal:
    return form(
        {"class": "v-block", "method": "get"},
        [row({}, [col({}, [SearchFormControls(field=args.search, placeholder=placeholder)])])],
    )
