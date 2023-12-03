import enum


@enum.verify(enum.UNIQUE)
class Shelves(enum.Enum):
    """
    Used to group individual shelves in form controls and the board layout.
    """

    UNDECIDED = ("Undecided", "outer-left")
    UPCOMING = ("Upcoming", "inner-left")
    PLAYING = ("Playing", "center")
    PAUSED = ("Paused", "inner-right")
    COMPLETED = ("Completed", "outer-right")

    def __new__(cls, value: str, column: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.column = column
        return obj


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

    UNSORTED = ("unsorted", "Unsorted", "Not assigned to a shelf yet", Shelves.UNDECIDED, False)
    UNRELEASED = ("unreleased", "Unreleased", "Waiting for release", Shelves.UNDECIDED, False)
    UNDECIDED = ("undecided", "Undecided", "Might read/play/watch in the future", Shelves.UNDECIDED)

    UPCOMING = ("upcoming", "Upcoming", "Might read/play/watch next", Shelves.UPCOMING)

    PLAYING = ("playing", "Playing", "Currently reading/playing/watching", Shelves.PLAYING)
    REPLAYING = ("replaying", "Replaying", "Returning to a completed work", Shelves.PLAYING, False)
    INFINITE = ("infinite", "Infinite", "An unending or long-term work", Shelves.PLAYING, False)

    PAUSED = ("paused", "Paused", "Might continue soon", Shelves.PAUSED)
    SHELVED = ("shelved", "Shelved", "Might continue one day", Shelves.PAUSED, False)
    REFERENCE = ("reference", "Reference", "Reference material with no status", Shelves.PAUSED, False)

    COMPLETED = ("completed", "Completed", "A completed work - well done!", Shelves.COMPLETED)
    ABANDONED = ("abandoned", "Abandoned", "Gave up on", Shelves.COMPLETED, False)

    title: str
    description: str
    shelves: Shelves
    show_if_empty: bool

    def __new__(cls, value: str, title: str, description: str, shelves: Shelves, show_if_empty: bool = True):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.title = title
        obj.description = description
        obj.shelves = shelves
        obj.show_if_empty = show_if_empty
        return obj
