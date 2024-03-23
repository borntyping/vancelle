from ...helpers import filter_empty_attributes
from ...types import Href, Hotmetal


def light_dark_img(
    light: Href,
    dark: Href,
    id: str | None = None,
    alt: str | None = None,
    width: int | None = None,
    height: int | None = None,
    style: str | None = None,
) -> Hotmetal:
    attrs = filter_empty_attributes(
        {
            "id": id,
            "src": light,
            "alt": alt,
            "width": str(width) if str else None,
            "height": str(height) if str else None,
            "style": style,
        }
    )
    return (
        "picture",
        {},
        [
            ("source", {"srcset": light, "media": "(prefers-color-scheme: light)"}, ()),
            ("source", {"srcset": dark, "media": "(prefers-color-scheme: dark)"}, ()),
            ("img", attrs, ()),
        ],
    )
