import enum
import typing


@enum.verify(enum.UNIQUE)
class ShelfGroup(enum.Enum):
    """
    Used to group individual shelves in form controls and the board layout.
    """

    UNDECIDED = ("undecided", "Undecided", "outer-left")
    UPCOMING = ("upcoming", "Upcoming", "inner-left")
    PLAYING = ("playing", "Playing", "center")
    PAUSED = ("paused", "Paused", "inner-right")
    COMPLETED = ("completed", "Completed", "outer-right")

    def __new__(cls, value: str, title: str, column: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.title = title
        obj.column = column
        return obj

    def shelves(self) -> typing.Sequence["Shelf"]:
        return [s for s in Shelf if s.group == self]


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

    UNSORTED = ("unsorted", "Unsorted", "Not assigned to a shelf yet", ShelfGroup.UNDECIDED, False)
    UNRELEASED = ("unreleased", "Unreleased", "Waiting for release", ShelfGroup.UNDECIDED, False)
    UNDECIDED = ("undecided", "Undecided", "Might read/play/watch in the future", ShelfGroup.UNDECIDED)

    UPCOMING = ("upcoming", "Upcoming", "Might read/play/watch next", ShelfGroup.UPCOMING)

    PLAYING = ("playing", "Playing", "Currently reading/playing/watching", ShelfGroup.PLAYING)
    REPLAYING = ("replaying", "Replaying", "Returning to a completed work", ShelfGroup.PLAYING, False)
    ONGOING = ("ongoing", "Ongoing", "A long-term or incomplete work", ShelfGroup.PLAYING, False)
    INFINITE = ("infinite", "Infinite", "A work that won't be completed", ShelfGroup.PLAYING, False)

    PAUSED = ("paused", "Paused", "Might continue soon", ShelfGroup.PAUSED)
    SHELVED = ("shelved", "Shelved", "Might continue one day", ShelfGroup.PAUSED, False)
    REFERENCE = ("reference", "Reference", "Reference material with no status", ShelfGroup.PAUSED, False)

    COMPLETED = ("completed", "Completed", "A completed work - well done!", ShelfGroup.COMPLETED)
    ABANDONED = ("abandoned", "Abandoned", "Gave up on", ShelfGroup.COMPLETED, False)

    title: str
    description: str
    group: ShelfGroup
    show_if_empty: bool

    def __new__(cls, value: str, title: str, description: str, group: ShelfGroup, show_if_empty: bool = True):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.title = title
        obj.description = description
        obj.group = group
        obj.show_if_empty = show_if_empty
        return obj
