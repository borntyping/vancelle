"""
https://getbootstrap.com/docs/5.3/forms/validation/#server-side
"""

import markupsafe
import wtforms
from wtforms.widgets import Input, Select, TextArea

from vancelle.html.helpers import html_classes


def form_control(field: wtforms.Field, *, label: bool = True, **kwargs) -> markupsafe.Markup:
    if label:
        label_element = field.label(class_="form-label")
    else:
        label_element = ""

    if field.errors:
        valid_classes = "is-invalid"
        valid_element = markupsafe.Markup(f'<div class="invalid-feedback">{' '.join(field.errors)}</div>')
    elif field.data and field.data != field.default:
        valid_classes = "is-valid"
        valid_element = markupsafe.Markup('<div class="valid-feedback">Looks good!</div>')
    else:
        valid_classes = ""
        valid_element = ""

    if isinstance(field.widget, (Input, TextArea)):
        widget_classes = "form-control"
    elif isinstance(field.widget, Select):
        widget_classes = "form-select"
    else:
        raise NotImplementedError

    # Avoid printing the string "None" as a placeholder.
    if "placeholder" in kwargs and kwargs["placeholder"] is None:
        del kwargs["placeholder"]

    field_classes = html_classes(widget_classes, valid_classes, kwargs.pop("class_", None))
    field_element = field(class_=field_classes, **kwargs)

    return label_element + field_element + valid_element
