import dataclasses
import typing
import datetime

import flask
import humanize
import inflect
import jinja2
import markupsafe
import wtforms.widgets

from ..inflect import p


def url_with(endpoint: str | None = None, **kwargs):
    endpoint = endpoint if endpoint else flask.request.endpoint
    values = flask.request.view_args | flask.request.args | kwargs  # type: ignore

    assert endpoint is not None
    return flask.url_for(endpoint=endpoint, **values)


@dataclasses.dataclass()
class ToggleItem:
    value: str
    title: str
    active: bool
    url: str


@dataclasses.dataclass()
class Toggle:
    mapping: typing.Mapping[str, str]

    key: str
    value: str | None
    default: str | None

    args: typing.Mapping[str, typing.Any]

    @classmethod
    def from_request(cls, mapping: typing.Mapping[str, str], key: str, *, default: str = "", **kwargs):
        if key in flask.request.args:
            value = flask.request.args[key]
        elif key in flask.request.cookies:
            value = flask.request.cookies[key]
        else:
            value = default

        if default == "":
            mapping = {"": "All", **mapping}

        return cls(mapping=mapping, key=key, value=value, default=default, args=kwargs)

    def __iter__(self) -> typing.Iterable[ToggleItem]:
        for value, title in self.mapping.items():
            yield ToggleItem(
                value=value,
                title=title,
                active=self.value == value,
                url=url_with(**self.args, **{self.key: value}),
            )

    def __html__(self) -> str:
        render = flask.get_template_attribute("components/toggle.html", "toggle")
        return render(definition=self)

    @property
    def title(self):
        return self.mapping[self.value]


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
        app.jinja_env.globals["html_params"] = self.html_params

    def count_plural(self, word: str, count: int) -> str:
        if not isinstance(count, int):
            raise ValueError("Count must be a number")

        return f"{count} {p.plural(word, count)}"

    def html_params(self, **kwargs: typing.Any) -> markupsafe.Markup:
        return markupsafe.Markup(wtforms.widgets.html_params(**kwargs))

    def filter_absent(self, value) -> str:
        return str(value) if value else self.ABSENT

    def filter_date(self, date: datetime.date | None, default: str = ABSENT) -> str:
        if date is None:
            return default

        if not isinstance(date, datetime.date):
            raise ValueError(f"Not a date: {date!r}")

        formatted = humanize.naturaldate(date)
        return markupsafe.Markup(f'<span class="x-has-tabular-nums" title="{date}">{formatted}</span>')

    def filter_exact_date(self, date: datetime.date | None) -> str:
        if date is None:
            return self.ABSENT

        if not isinstance(date, datetime.date):
            raise ValueError("Not a date")

        return markupsafe.Markup(f'<span class="x-has-tabular-nums">{date}</span>')

    def filter_datetime(self, d: datetime.datetime | None) -> str:
        return humanize.naturaltime(d) if d else self.ABSENT

    def filter_inflect_join(self, words: typing.Iterable[inflect.Word]) -> str:
        return p.join(words=list(words))
