import inflect

p = inflect.engine()


def count_plural(word: str, count: int) -> str:
    if not isinstance(count, int):
        raise ValueError("Count must be a number")

    return f"{count} {p.plural(word, count)}"
