import dataclasses
import typing
import datetime

import flask
import humanize
import inflect
import jinja2
import markupsafe
import structlog
import wtforms.widgets

from ..inflect import p

logger = structlog.get_logger(logger_name=__name__)


def url_with(endpoint: str | None = None, **kwargs):
    """Like url_for(), but keeps parameters from the current request."""
    endpoint = endpoint if endpoint else flask.request.endpoint
    values = flask.request.view_args | flask.request.args | kwargs  # type: ignore

    assert endpoint is not None
    return flask.url_for(endpoint=endpoint, **values)


def compare_endpoints(
    *,
    request_endpoint: str,
    request_args: dict,
    other_endpoint: str,
    other_args: dict,
) -> bool:
    """Testable implementation of 'url_is_active()'."""
    result = request_endpoint == other_endpoint and all(request_args.get(k) == v for k, v in other_args.items())
    logger.debug(
        "compare_endpoints()",
        request_endpoint=request_endpoint,
        request_args=request_args,
        other_endpoint=other_endpoint,
        other_args=other_args,
        result=result,
    )
    return request_endpoint == other_endpoint and all(request_args.get(k) == v for k, v in other_args.items())


def url_is_active(endpoint: str, **kwargs: typing.Any) -> bool:
    """
    Compare an endpoint and it's arguments to the current request, returning true if they match.

    `/works/?work_type='books'&work_shelf='upcoming'` should match `url_is_active('works.index', work_type='books')`.
    """

    return compare_endpoints(
        request_endpoint=flask.request.endpoint,
        request_args=flask.request.view_args | flask.request.args,
        other_endpoint=endpoint,
        other_args=kwargs,
    )


@dataclasses.dataclass()
class ToggleItem:
    value: str
    title: str
    active: bool
    url: str


@dataclasses.dataclass()
class Toggle:
    mapping: typing.Mapping[str, str] = dataclasses.field(repr=False)
    default: str

    def __init__(self, mapping: typing.Mapping[str, str], default: str = ""):
        if not default:
            mapping = {"": "All", **mapping}

        self.mapping = mapping
        self.default = default

    def from_request(self, key: str, clear: typing.Sequence[str] = ()) -> "ToggleState":
        if key in flask.request.args:
            value = flask.request.args[key]
        elif key in flask.request.cookies:
            value = flask.request.cookies[key]
        else:
            value = self.default

        return ToggleState(key=key, value=value, clear=clear, toggle=self)


@dataclasses.dataclass()
class ToggleState:
    key: str
    value: str

    clear: typing.Sequence[str]
    toggle: Toggle

    def __iter__(self) -> typing.Iterable[ToggleItem]:
        for value, title in self.toggle.mapping.items():
            yield ToggleItem(
                value=value,
                title=title,
                active=self.value == value,
                url=url_with(**{key: None for key in self.clear}, **{self.key: value}),
            )

    def __html__(self) -> str:
        render = flask.get_template_attribute("components/toggle.html", "toggle")
        return render(definition=self)

    @property
    def title(self):
        return self.toggle.mapping[self.value]


@dataclasses.dataclass()
class HtmlExtension:
    ABSENT = "—"

    def init_app(self, app: flask.Flask) -> None:
        app.jinja_env.undefined = jinja2.StrictUndefined

        app.jinja_env.filters["absent"] = self.filter_absent
        app.jinja_env.filters["date"] = self.filter_date
        app.jinja_env.filters["datetime"] = self.filter_datetime
        app.jinja_env.filters["exact_date"] = self.filter_exact_date
        app.jinja_env.filters["inflect_join"] = self.filter_inflect_join

        app.jinja_env.globals["absent"] = self.ABSENT
        app.jinja_env.globals["n"] = self.count_plural
        app.jinja_env.globals["p"] = p
        app.jinja_env.globals["url_with"] = url_with
        app.jinja_env.globals["url_is_active"] = url_is_active
        app.jinja_env.globals["html_params"] = self.html_params

    def count_plural(self, word: str, count: int) -> str:
        if not isinstance(count, int):
            raise ValueError("Count must be a number")

        return f"{count} {p.plural(word, count)}"

    def html_params(self, **kwargs: typing.Any) -> markupsafe.Markup:
        return markupsafe.Markup(wtforms.widgets.html_params(**kwargs))

    def filter_absent(self, value) -> str:
        return str(value) if value else self.ABSENT

    def filter_date(self, date: datetime.date | None) -> str:
        if not isinstance(date, datetime.date):
            raise ValueError(f"Not a date: {date!r}")

        formatted = humanize.naturaldate(date)
        return markupsafe.Markup(f'<span class="x-has-tabular-nums" title="{date}">{formatted}</span>')

    def filter_exact_date(self, date: datetime.date | None) -> str:
        if date is None:
            return self.ABSENT

        if not isinstance(date, datetime.date):
            raise ValueError("Not a date")

        formatted = humanize.naturaldate(date)
        return markupsafe.Markup(f'<span class="x-has-tabular-nums" title="{formatted}">{date}</span>')

    def filter_datetime(self, d: datetime.datetime | None) -> str:
        return humanize.naturaltime(d) if d else self.ABSENT

    def filter_inflect_join(self, words: typing.Iterable[inflect.Word]) -> str:
        return p.join(words=list(words))
