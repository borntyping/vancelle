import flask

from vancelle.lib.heavymetal import Heavymetal


def bi_font(name: str) -> Heavymetal:
    """
    The font icons seem to render in odd positions below the baseline when used in text.
    Fixed in 'static/src/ext/bootstrap-icons/'.

    >>> from vancelle.lib.heavymetal import render
    >>> render(bi_font("bootstrap"))
    Markup('<i class="bi bi-bootstrap"></i>')
    """
    return ("i", {"class": f"bi bi-{name}"}, [])


def bi_svg(name: str) -> Heavymetal:
    """
    The SVG icons seem to render below the baseline when used in buttons.

    <svg class="bi" width="1em" height="1em" fill="currentColor">
      <use xlink:href="bootstrap-icons.svg#heart-fill"/>
    </svg>
    """
    url = flask.url_for("static", filename="dist/bootstrap-icons/bootstrap-icons.svg")
    return (
        "svg",
        {"class": "bi", "height": "1em", "width": "1em", "fill": "currentColor", "aria-hidden": "true"},
        (("use", {"xlink:href": f"{url}#{name}"}, ()),),
    )
