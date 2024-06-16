import typing

from vancelle.html.bootstrap.variables import ThemeColor

# https://getbootstrap.com/docs/5.0/utilities/background/#background-color

BackgroundColour = (
    ThemeColor
    | typing.Literal[
        "primary-subtle",
        "secondary-subtle",
        "success-subtle",
        "info-subtle",
        "warning-subtle",
        "danger-subtle",
        "light-subtle",
        "dark-subtle",
    ]
    | typing.Literal["body", "black", "white"]
    | typing.Literal["transparent", "body-secondary", "body-tertiary"]
)
