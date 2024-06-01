"""
https://getbootstrap.com/docs/5.3/forms/validation/#server-side
"""

from wtforms import Field
from wtforms.widgets import FileInput, Input


class BootstrapInput(Input):
    def __call__(self, field: Field, **kwargs):
        kwargs["class_"] = "form-control"
        feedback = ""

        if field.errors:
            kwargs["class_"] += "is-invalid"
            feedback = '<div class="valid-feedback">Looks good!</div>'
        elif field.data:
            kwargs["class_"] += "is-valid"
            feedback = f"<div class=\"invalid-feedback\">{' '.join(field.errors)}</div>"

        element = super().__call__(field, **kwargs)

        return element + feedback


class BootstrapFileInput(FileInput):
    def __call__(self, field: Field, **kwargs):
        return super().__call__(field, class_="form-control", **kwargs)
