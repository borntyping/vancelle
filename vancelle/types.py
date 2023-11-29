import enum
import typing

from vancelle.extensions.ext_html import p


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

    UNSORTED = ("unsorted", "Unsorted", "Not assigned to a shelf yet")
    UNRELEASED = ("unreleased", "Unreleased", "Waiting for release")
    UNDECIDED = ("undecided", "Undecided", "Might read/play/watch in the future")
    UPCOMING = ("upcoming", "Upcoming", "Might read/play/watch next")

    PLAYING = ("playing", "Playing", "Currently reading/playing/watching")
    REPLAYING = ("replaying", "Replaying", "Returning to a completed work")
    INFINITE = ("infinite", "Infinite", "An unending or long-term work")
    PAUSED = ("paused", "Paused", "Might continue soon")
    SHELVED = ("shelved", "Shelved", "Might continue one day")

    COMPLETED = ("completed", "Completed", "Reached the end")
    ABANDONED = ("abandoned", "Abandoned", "Gave up on")

    def __new__(cls, value: str, title: str, description: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.title = title
        obj.description = description
        return obj


#
#
# @enum.verify(enum.UNIQUE)
# class WorkType(enum.Enum):
#     """
#     >>> WorkType('game')
#     <WorkType.GAME: 'game'>
#     >>> WorkType.GAME.value
#     'game'
#     >>> WorkType.GAME.title
#     'Game'
#     >>> WorkType.GAME.plural
#     'games'
#     """
#
#     BOOK = ("book",)
#     GAME = ("game",)
#     FILM = ("film",)
#     SHOW = ("show", None, "TV show")
#
#     BOARDGAME = ("boardgame", "board game")
#     MUSIC = ("music",)
#
#     def __new__(cls, value: str, noun: str = None, title: str = None):
#         obj = object.__new__(cls)
#         obj._value_ = value
#         obj.noun = noun or value
#         obj.title = title or obj.noun.capitalize()
#         obj.plural = p.plural(obj.noun)
#         return obj
