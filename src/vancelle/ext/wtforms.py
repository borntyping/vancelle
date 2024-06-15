class NullFilter:
    def __call__(self, value: str | None) -> str | None:
        return value if value else None
