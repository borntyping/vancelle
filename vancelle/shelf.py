import enum
import typing


@enum.verify(enum.UNIQUE)
class Shelf(enum.Enum):
    """
    >>> Shelf('unsorted')
    <Shelf.UNSORTED: 'unsorted'>
    >>> Shelf.UNSORTED.value
    'unsorted'
    >>> Shelf.UNSORTED.title
    'Unsorted'
    >>> Shelf.UNSORTED.description
    'Not assigned to a shelf yet'
    """

    UNSORTED = ("unsorted", "Unsorted", "Not assigned to a shelf yet", "Undecided", False)
    UNRELEASED = ("unreleased", "Unreleased", "Waiting for release", "Undecided", False)
    UNDECIDED = ("undecided", "Undecided", "Might read/play/watch in the future", "Undecided")

    UPCOMING = ("upcoming", "Upcoming", "Might read/play/watch next", "Upcoming")

    PLAYING = ("playing", "Playing", "Currently reading/playing/watching", "Playing")
    REPLAYING = ("replaying", "Replaying", "Returning to a completed work", "Playing", False)
    ONGOING = ("ongoing", "Ongoing", "A long-term or incomplete work", "Playing", False)
    INFINITE = ("infinite", "Infinite", "A work that won't be completed", "Playing", False)

    PAUSED = ("paused", "Paused", "Might continue soon", "Paused")
    SHELVED = ("shelved", "Shelved", "Might continue one day", "Paused", False)
    REFERENCE = ("reference", "Reference", "Reference material with no status", "Paused", False)

    COMPLETED = ("completed", "Completed", "A completed work - well done!", "Completed")
    ABANDONED = ("abandoned", "Abandoned", "Gave up on", "Completed", False)

    title: str
    description: str
    group: str
    show_if_empty: bool

    def __new__(cls, value: str, title: str, description: str, group: str, show_if_empty: bool = True):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.title = title
        obj.description = description
        obj.group = group
        obj.show_if_empty = show_if_empty
        return obj


@enum.verify(enum.UNIQUE)
class Case(enum.Enum):
    """Used to group shelves for display."""

    UPCOMING = ("upcoming", "Upcoming", (Shelf.UPCOMING, Shelf.UNRELEASED, Shelf.UNDECIDED))
    PLAYING = ("playing", "Playing", (Shelf.PLAYING, Shelf.REPLAYING, Shelf.ONGOING, Shelf.INFINITE))
    PAUSED = ("paused", "Paused", (Shelf.PAUSED, Shelf.SHELVED))
    COMPLETED = ("completed", "Completed", (Shelf.COMPLETED, Shelf.ABANDONED))
    OTHER = ("other", "Other", (Shelf.UNSORTED, Shelf.REFERENCE))

    def __new__(cls, value: str, title: str, shelves: typing.Tuple[Shelf, ...]):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.title = title
        obj.shelves = shelves
        return obj
