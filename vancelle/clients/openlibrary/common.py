import typing


T = typing.TypeVar("T")


def first_or_none(seq: typing.Sequence[T]) -> T | None:
    return [*seq, None][0]


def first_or_error(seq: typing.Sequence[T]) -> T | None:
    if len(seq) < 1:
        raise Exception("Sequence has no items")

    if len(seq) > 1:
        raise Exception(f"Sequence {seq!r} has multiple items")

    return seq[0]
