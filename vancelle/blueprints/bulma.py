import typing

import flask
import markupsafe
import structlog
import wtforms.widgets

logger = structlog.get_logger(logger_name=__name__)

bp = flask.Blueprint("bulma", __name__)


def join(string: str, value: str) -> str:
    if not string or string[-1] == " ":
        return string + value

    return string + " " + value


class BulmaSelect(wtforms.widgets.Select):
    """Wrap <select> in <div class="select ...">."""

    def __call__(self, field: wtforms.SelectField, **kwargs) -> str:
        """
        Warning: kwargs will have trailing underscores stripped. This is because
        wtforms `render_field` calls `clean_key()` even though it will be called
        again by `html_params` later.
        """
        logger.debug("BulmaSelect", field=field, kwargs=kwargs)

        class_: str = kwargs.pop("class", "select is-fullwidth")
        input_class_: str | False = kwargs.pop("input_class", False)

        markup = super().__call__(field=field, class_=input_class_, **kwargs)
        return markupsafe.Markup(f"<div {wtforms.widgets.html_params(class_=class_)}>{markup}</div>")


def macro(attribute, **kwargs) -> markupsafe.Markup:
    return flask.get_template_attribute("components/bulma.html", attribute)(**kwargs)


@bp.app_template_global()
def bulma_widget(field: wtforms.FormField, **kwargs: typing.Any) -> str:
    """
    Render a wtforms field.

    I call it a widget here to avoid confusion with the bulma "field" and "control" elements.
    """
    logger.debug("bulma_widget", field=field, kwargs=kwargs)
    class_ = kwargs.pop("class_", "")

    match field.__class__:
        case wtforms.TextAreaField:
            class_ = join(class_, "textarea")
        case wtforms.SelectField:
            class_ = join(class_, "select is-fullwidth")
        case wtforms.BooleanField:
            raise NotImplementedError
        case _:
            class_ = join(class_, "input")

    if field.errors:
        class_ = join(class_, "is-danger")
    elif field.data and field.data != field.default:
        class_ = join(class_, "is-success")

    # Avoid printing the string "None" as a placeholder.
    if "placeholder" in kwargs and kwargs["placeholder"] is None:
        del kwargs["placeholder"]

    return field(class_=class_, **kwargs)


@bp.app_template_global()
def bulma_form_field(field: wtforms.FormField, **kwargs: typing.Any) -> str:
    return macro("bulma_form_field", field=field, **kwargs)
