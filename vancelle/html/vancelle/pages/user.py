import dataclasses
import typing

import flask
import flask_login

from vancelle.forms.user import ImportForm, LoginForm
from vancelle.html.bulma.columns import columns
from vancelle.html.bulma.elements.box import box
from vancelle.html.bulma.form.file import bulma_file_input
from vancelle.html.bulma.form.general import form_field
from vancelle.html.document import a, button, code, div, form, h2, p
from vancelle.html.hotmetal import Hotmetal
from vancelle.html.vancelle.components.header import heading, block_section
from vancelle.html.vancelle.pages.base import page
from vancelle.inflect import p as inf


def login_page(login_form: LoginForm) -> Hotmetal:
    return page(
        div(
            {"class": "container is-max-desktop"},
            [
                form(
                    {"action": flask.url_for("user.login"), "method": "POST", "class": "box"},
                    [
                        form_field(login_form.csrf_token),
                        form_field(login_form.username, placeholder="Username"),
                        form_field(login_form.password, placeholder="Password"),
                        button({"class": "button", "type": "submit"}, ["Login"]),
                    ],
                ),
            ],
        )
    )


@dataclasses.dataclass()
class ProfilePage:
    import_form: ImportForm
    work_count: int
    filename: str

    def __call__(self, context: typing.Any) -> Hotmetal:
        return page(
            block_section(
                heading("User profile", f"@{flask_login.current_user.username}"),
                columns(self.import_box(), self.export_box()),
            )
        )

    def import_box(self) -> Hotmetal:
        error_elements = [p({"class": "help is-danger"}, [str(error)]) for error in self.import_form.backup.errors]
        import_button = button({"class": "button", "type": "submit", "disabled": self.work_count > 0}, ["Import"])

        if self.work_count > 0:
            description_p = p(
                {"class": "block has-text-danger"},
                [f"Import is disabled, you already have {self.work_count} {inf.plural('work', self.work_count)}."],
            )
        else:
            description_p = p({"class": "block"}, [f"Import from a ", code({}, self.filename), " file."])

        return box(
            h2({"class": "title is-5"}, ["Import data"]),
            description_p,
            form(
                {"action": flask.url_for("user.import"), "method": "POST", "enctype": "multipart/form-data"},
                [
                    form_field(self.import_form.csrf_token),
                    div(
                        {"class": "field is-grouped"},
                        [
                            div({"class": "control is-expanded"}, [bulma_file_input(self.import_form.backup.name)]),
                            div({"class": "control"}, [import_button]),
                            *error_elements,
                        ],
                    ),
                ],
            ),
        )

    def export_box(self) -> Hotmetal:
        return box(
            h2({"class": "title is-5"}, ["Export data"]),
            p(
                {"class": "block"},
                [f"Export {self.work_count} {inf.plural('work', self.work_count)} to a ", code({}, self.filename), " file."],
            ),
            a({"href": flask.url_for("user.export"), "class": "button is-primary"}, ["Export"]),
        )
