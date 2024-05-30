import typing

import markupsafe
import structlog
import wtforms
import wtforms.csrf.core

from vancelle.html.bulma.elements.icon import icon
from vancelle.html.helpers import html_classes
from vancelle.lib.heavymetal import Heavymetal, HeavymetalElement
from vancelle.lib.heavymetal.html import p

logger = structlog.get_logger(logger_name=__name__)


def _render(field: wtforms.FormField, **kwargs: typing.Any) -> str:
    """Render a wtforms field, adding bulma classes if necessary."""
    classes = [kwargs.pop("class_", None)]

    match field.__class__:
        case wtforms.TextAreaField:
            classes.append("textarea")
        case wtforms.SelectField:
            classes.append("select")
            classes.append("is-fullwidth")
        case wtforms.BooleanField:
            raise NotImplementedError
        case _:
            classes.append("input")

    if field.errors:
        classes.append("is-error")
    elif field.data and field.data != field.default:
        classes.append("is-success")

    # Avoid printing the string "None" as a placeholder.
    if "placeholder" in kwargs and kwargs["placeholder"] is None:
        del kwargs["placeholder"]

    return str(field(class_=html_classes(*classes), **kwargs))


def form_field(
    field: wtforms.FormField,
    *,
    label: bool = True,
    icon_left: str | None = None,
    icon_right: str | None = None,
    **kwargs: typing.Any,
) -> Heavymetal:
    if isinstance(field, wtforms.csrf.core.CSRFTokenField):
        return markupsafe.Markup(field)

    input_element = markupsafe.Markup(_render(field, **kwargs))

    control_element = HeavymetalElement("div", {"class": "control"}, [input_element])
    if icon_left:
        control_element.attrs["class"] += " has-icons-left"
        control_element.children.append(icon(icon_left, "is-small", "is-left"))
    if icon_right:
        control_element.attrs["class"] += " has-icons-right"
        control_element.children.append(icon(icon_right, "is-small", "is-right"))

    field_element = HeavymetalElement("div", {"class": "field"}, [control_element])
    if label:
        field_element.children.insert(0, field.label(class_="label"))
    for error in field.errors:
        field_element.children.append(p({"class": "help is-danger"}, [str(error)]))

    return field_element
