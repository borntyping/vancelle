import enum
from typing import Self

from vancelle.extensions.ext_html import p


@enum.verify(enum.UNIQUE)
class Shelf(enum.StrEnum):
    """
    >>> Shelf.UNRELEASED.value
    'unreleased'
    >>> Shelf.UNRELEASED.title
    'Unreleased'
    >>> Shelf.UNRELEASED.description
    'Waiting for release'
    """

    UNSORTED = enum.member("unsorted")
    UNRELEASED = enum.member("unreleased")
    UNDECIDED = enum.member("undecided")
    UPCOMING = enum.member("upcoming")

    PLAYING = enum.member("playing")
    INFINITE = enum.member("infinite")
    PAUSED = enum.member("paused")
    SHELVED = enum.member("shelved")

    COMPLETED = enum.member("completed")
    ABANDONED = enum.member("abandoned")

    titles: dict[Self, str] = enum.nonmember(
        {
            UNSORTED: "Unsorted",
            UNRELEASED: "Unreleased",
            UNDECIDED: "Undecided",
            UPCOMING: "Upcoming",
            PLAYING: "Playing",
            INFINITE: "Infinite",
            PAUSED: "Paused",
            SHELVED: "Shelved",
            COMPLETED: "Completed",
            ABANDONED: "Abandoned",
        }
    )

    descriptions: dict[Self, str] = enum.nonmember(
        {
            UNSORTED: "Not assigned to a shelf yet",
            UNRELEASED: "Waiting for release",
            UNDECIDED: "Might read/play/watch in the future",
            UPCOMING: "Might read/play/watch next",
            PLAYING: "Currently reading/playing/watching",
            INFINITE: "Always reading/playing/watching",
            PAUSED: "Might continue soon",
            SHELVED: "Might continue one day",
            COMPLETED: "Reached the end",
            ABANDONED: "Gave up on",
        }
    )

    @enum.property
    def title(self) -> str:
        return self.titles[self.value]

    @enum.property
    def description(self) -> str:
        return self.descriptions[self.value]


class WorkType(enum.StrEnum):
    BOOK = "book"
    GAME = "game"
    FILM = "film"
    SHOW = "show"

    BOARDGAME = "boardgame"
    MUSIC = "music"

    nouns: dict[Self, str] = enum.nonmember({BOARDGAME: "Board game"})

    @enum.property
    def noun(self) -> str:
        return self.nouns.get(self.value, self.value)

    titles: dict[Self, str] = enum.nonmember({SHOW: "TV show"})

    @enum.property
    def title(self) -> str:
        return self.titles.get(self.noun, self.noun.capitalize())

    @enum.property
    def plural(self) -> str:
        return p.plural(self.noun)
