from ...hotmetal import Hotmetal, element


def light_dark_img(
    light: str,
    dark: str,
    id: str | None = None,
    alt: str | None = None,
    width: int | None = None,
    height: int | None = None,
    style: str | None = None,
) -> Hotmetal:
    img_attrs = {
        "id": id,
        "src": light,
        "alt": alt,
        "width": str(width) if str else None,
        "height": str(height) if str else None,
        "style": style,
    }
    return element(
        "picture",
        {},
        [
            element("source", {"srcset": light, "media": "(prefers-color-scheme: light)"}, ()),
            element("source", {"srcset": dark, "media": "(prefers-color-scheme: dark)"}, ()),
            element("img", img_attrs, ()),
        ],
    )
