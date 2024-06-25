import dataclasses
import typing

from vancelle.html.vancelle.components.layout import PageHeader
from vancelle.html.vancelle.components.optional import quote
from vancelle.html.vancelle.components.panel import DetailsPanel, PanelControl
from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import a, code, fragment, p
from vancelle.models import Entry
from vancelle.models.details import Details
from vancelle.models.properties import Properties


def EntryPageHeader(entry: Entry) -> Heavymetal:
    return PageHeader(entry.resolve_title(), entry.resolve_subtitle())


@dataclasses.dataclass()
class EntryDetailsPanel(DetailsPanel):
    entry: Entry

    def id(self) -> str:
        return f"entry-{self.entry.id}"

    def cover(self) -> str | None:
        return self.entry.url_for_cover()

    def background(self) -> str | None:
        return self.entry.url_for_background()

    def details(self) -> Details:
        return self.entry.into_details()

    def properties(self) -> Properties:
        return list(self.entry.into_properties())

    def type_properties(self) -> Properties:
        return list(self.entry.info.into_properties())

    def data(self) -> str | None:
        return self.entry.data

    def controls(self) -> typing.Sequence[PanelControl]:
        yield PanelControl(
            href=self.entry.url_for(),
            icon="database",
            name="Permalink",
            title="Permalink.",
        )

        if self.entry.info.is_external_source:
            yield PanelControl(
                post=True,
                href=self.entry.url_for_refresh(),
                icon="arrow-clockwise",
                name="Refresh",
                title="Update this entry from it's source.",
            )

        if self.entry.deleted:
            yield PanelControl(
                post=True,
                href=self.entry.url_for_restore(),
                icon="trash",
                name="Restore",
                title="Restore this entry.",
                button_classes="text-success",
            )
            yield PanelControl(
                post=True,
                href=self.entry.url_for_permanently_delete(),
                name="Permanently delete",
                icon="trash",
                title=(
                    "Delete this entry. "
                    "It will not be possible to recover these details without fetching them from the original source."
                ),
                button_classes="text-danger",
            )

        else:
            yield PanelControl(
                post=True,
                href=self.entry.url_for_delete(),
                icon="trash",
                name="Delete",
                title="Delete this entry. You will be able to restore it.",
            )

        if self.entry.work:
            yield PanelControl(
                href=self.entry.work.url_for(),
                icon="easel",
                name="View linked work",
                title="View the work linked to this entry.",
            )

    def description(self) -> Heavymetal:
        link = a(
            {
                "class": "link-body-emphasis",
                "href": self.entry.external_url(),
                "rel": "noopener noreferrer nofollow",
                "target": "_blank",
            },
            [f"{self.entry.info.noun_full} ", code({}, self.entry.id)],
        )
        released = [f", released {self.entry.release_date}"] if self.entry.release_date else []
        description = p({}, [link, *released, "."])

        attached_to = (
            p(
                {},
                [
                    "Attached to ",
                    quote([a({"href": self.entry.work.url_for()}, [self.entry.work.resolve_details().title])]),
                    ".",
                ],
            )
            if self.entry.work
            else ...
        )

        return fragment([description, attached_to])
