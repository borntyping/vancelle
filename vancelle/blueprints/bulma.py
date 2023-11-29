import typing

import flask
import markupsafe
import wtforms.widgets

bp = flask.Blueprint("bulma", __name__)


def join(string: str, value: str) -> str:
    if not string or string[-1] == " ":
        return string + value

    return string + " " + value


class BulmaSelect(wtforms.widgets.Select):
    def __call__(self, field: wtforms.SelectField, **kwargs) -> str:
        """Wrap <select> in <div class="select">."""
        wrapper = kwargs.pop("wrapper", {})
        markup = super().__call__(field=field, **kwargs)

        class_ = wrapper.pop("class_", "")
        class_ = join(class_, "select")

        if wrapper.get("fullwidth", True):
            class_ = join(class_, "is-fullwidth")

        wrapper_params = wtforms.widgets.html_params(class_=class_, **wrapper)
        return markupsafe.Markup(f"<div {wrapper_params}>{markup}</div>")


@bp.app_template_global()
def bulma_field_params(
    field: wtforms.FormField,
    **kwargs: typing.Any,
) -> typing.Mapping[str, typing.Any]:
    class_ = kwargs.pop("class_", "")

    match field.__class__:
        case wtforms.TextAreaField:
            class_ = join(class_, "textarea")
        case wtforms.SelectField:
            class_ = join(class_, "select")
        case wtforms.BooleanField:
            raise NotImplementedError
        case _:
            class_ = join(class_, "input")

    if field.errors:
        class_ = join(class_, "is-danger")

    # Avoid printing the string "None" as a placeholder.
    if "placeholder" in kwargs and kwargs["placeholder"] is None:
        del kwargs["placeholder"]

    if "wrapper" in kwargs:
        del kwargs["wrapper"]

    return kwargs | {"class_": class_}


@bp.app_template_global()
def bulma_control_params(
    field: wtforms.FormField,
    icon_left: str | None = None,
    icon_right: str | None = None,
    **kwargs,
) -> typing.Mapping[str, typing.Any]:
    classes = ["control"]

    if isinstance(field, wtforms.SelectField) and kwargs.get("fullwidth", True):
        classes.append("is-expanded")

    if field.errors:
        classes.append("is-danger")

    if icon_left:
        classes.append("has-icons-left")

    if icon_right:
        classes.append("has-icons-right")

    return {"class_": " ".join(classes)}
