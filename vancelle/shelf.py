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

    UNSORTED = ("unsorted", "Unsorted", "Not assigned to a shelf yet.", "Undecided")
    UNRELEASED = ("unreleased", "Unreleased", "Waiting for release.", "Undecided")
    UNDECIDED = ("undecided", "Undecided", "Might read/play/watch in the future.", "Undecided", True)

    UPCOMING = ("upcoming", "Upcoming", "Coming up next.", "Upcoming", True)
    RETURNING = ("returning", "Returning", "A repeat of a completed work.", "Upcoming")

    PLAYING = ("playing", "Playing", "Currently reading/playing/watching.", "Playing", True)
    REPLAYING = ("replaying", "Replaying", "Returning to a completed work.", "Playing")
    ONGOING = ("ongoing", "Ongoing", "A long-term or incomplete work.", "Playing")
    INFINITE = ("infinite", "Infinite", "A work that won't be completed.", "Playing")

    PAUSED = ("paused", "Paused", "Might continue soon.", "Paused", True)
    SHELVED = ("shelved", "Shelved", "Might continue one day.", "Paused")
    REFERENCE = ("reference", "Reference", "Reference material with no status.", "Paused")

    COMPLETED = ("completed", "Completed", "A completed work.", "Completed", True)
    ABANDONED = ("abandoned", "Abandoned", "Gave up on.", "Completed")
    UNTOUCHED = ("untouched", "Untouched", "Never started.", "Completed")

    title: str
    description: str
    group: str
    show_if_empty: bool

    def __new__(cls, value: str, title: str, description: str, group: str, show_if_empty: bool = False):
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
