""" """

import markupsafe
import wtforms
from wtforms.widgets import CheckboxInput, RadioInput, Select

from vancelle.lib.html import html_classes


def _form_control_validation_class(field: wtforms.Field) -> str:
    if field.errors:
        return "is-invalid"

    if field.data and field.data != field.default:
        return "is-valid"

    return ""


def _form_control_validation_element(field: wtforms.Field) -> str:
    return f'<div class="invalid-feedback">{' '.join(field.errors)}</div>' if field.errors else ""


def form_control(field: wtforms.Field, *, label: bool = True, validation: bool = True, **kwargs) -> markupsafe.Markup:
    """
    Render a wtforms field as a Bootstrap 5 field.

    https://getbootstrap.com/docs/5.3/forms/validation/#server-side

    """
    if isinstance(field.widget, (CheckboxInput, RadioInput)):
        raise ValueError("Use form_control_check() instead")

    # Avoid printing the string "None" as a placeholder.
    if "placeholder" in kwargs and kwargs["placeholder"] is None:
        del kwargs["placeholder"]

    if isinstance(field.widget, Select):
        widget_classes = "form-select"
    else:
        widget_classes = "form-control"

    valid_classes = _form_control_validation_class(field) if validation else ""
    field_classes = html_classes(widget_classes, valid_classes, kwargs.pop("class_", None))

    label_element = field.label() if label else ""
    field_element = field.widget(field, class_=field_classes, **kwargs)
    valid_element = _form_control_validation_element(field) if validation else ""

    return markupsafe.Markup(f"{label_element}{field_element}{valid_element}")


def form_control_check(field: wtforms.BooleanField, *, switch: bool = False, **kwargs) -> markupsafe.Markup:
    """
    https://getbootstrap.com/docs/5.3/forms/checks-radios/
    """

    if not isinstance(field.widget, (CheckboxInput, RadioInput)):
        raise ValueError("form_control_check requires a checkbox or radio input")

    valid_classes = _form_control_validation_class(field)
    field_classes = html_classes("form-check-input", valid_classes, kwargs.pop("class_", None))
    check_classes = html_classes("form-check", {"form-switch": switch})

    field_element = field(class_=field_classes, **kwargs)
    label_element = field.label(class_="form-check-label mb-0")
    valid_element = _form_control_validation_element(field)
    check_element = f'<div class="{check_classes}">{field_element}{label_element}{valid_element}</div>'

    return markupsafe.Markup(check_element)
