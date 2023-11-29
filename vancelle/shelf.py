import enum


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

    UNSORTED = ("unsorted", "Unsorted", "Not assigned to a shelf yet", "outer-left", False)
    UNRELEASED = ("unreleased", "Unreleased", "Waiting for release", "outer-left")
    UNDECIDED = ("undecided", "Undecided", "Might read/play/watch in the future", "outer-left")
    UPCOMING = ("upcoming", "Upcoming", "Might read/play/watch next", "inner-left")

    PLAYING = ("playing", "Playing", "Currently reading/playing/watching", "center")
    REPLAYING = ("replaying", "Replaying", "Returning to a completed work", "center", False)
    INFINITE = ("infinite", "Infinite", "An unending or long-term work", "center", False)

    PAUSED = ("paused", "Paused", "Might continue soon", "inner-right", False)
    SHELVED = ("shelved", "Shelved", "Might continue one day", "inner-right")
    REFERENCE = ("reference", "Reference", "Reference material with no status", "inner-right")

    COMPLETED = ("completed", "Completed", "A completed work - well done!", "outer-right")
    ABANDONED = ("abandoned", "Abandoned", "Gave up on", "outer-right")

    title: str
    description: str
    column: str
    show_if_empty: bool

    def __new__(
        cls,
        value: str,
        title: str,
        description: str,
        column: str,
        show_if_empty: bool = True,
    ):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.title = title
        obj.description = description
        obj.column = column
        obj.show_if_empty = show_if_empty
        return obj
