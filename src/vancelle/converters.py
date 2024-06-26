import typing

import werkzeug.routing

from vancelle.models import Entry, Work


class WorkTypeConverter(werkzeug.routing.BaseConverter):
    def to_python(self, value: str) -> typing.Type[Work]:
        return Work.get_subclass(value)

    def to_url(self, value: str | typing.Type[Work]) -> str:
        return value.polymorphic_identity()


class EntryTypeConverter(werkzeug.routing.BaseConverter):
    def to_python(self, value: str) -> typing.Type[Entry]:
        return Entry.get_subclass(value)

    def to_url(self, value: typing.Type[Entry]) -> str:
        return value.polymorphic_identity()
