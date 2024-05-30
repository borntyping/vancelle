from vancelle.lib.heavymetal import Heavymetal
from vancelle.lib.heavymetal.html import img, picture, source


def light_dark_img(
    light: str,
    dark: str,
    id: str | None = None,
    alt: str | None = None,
    width: int | None = None,
    height: int | None = None,
    style: str | None = None,
) -> Heavymetal:
    return picture(
        {},
        [
            source({"srcset": light, "media": "(prefers-color-scheme: light)"}),
            source({"srcset": dark, "media": "(prefers-color-scheme: dark)"}),
            img(
                {
                    "id": id,
                    "src": light,
                    "alt": alt,
                    "width": str(width) if str else None,
                    "height": str(height) if str else None,
                    "style": style,
                }
            ),
        ],
    )
