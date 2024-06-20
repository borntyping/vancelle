import dataclasses

import flask
import flask_login

from vancelle.forms.user import ImportForm, LoginForm
from vancelle.html.bootstrap.forms.controls import form_control
from vancelle.html.vancelle.components.header import page_header, section_header
from vancelle.html.vancelle.pages.base import page
from vancelle.inflect import p as inf
from vancelle.lib.heavymetal import Heavymetal, HeavymetalComponent
from vancelle.lib.heavymetal.html import a, button, code, div, form, p, section


@dataclasses.dataclass()
class LoginPage(HeavymetalComponent):
    login_form: LoginForm

    def heavymetal(self) -> Heavymetal:
        return page(
            [
                div(
                    {"class": "container is-max-desktop"},
                    [
                        form(
                            {"action": flask.url_for("user.login"), "method": "POST", "class": "box"},
                            [
                                form_control(self.login_form.csrf_token),
                                form_control(self.login_form.username, placeholder="Username"),
                                form_control(self.login_form.password, placeholder="Password"),
                                button({"class": "btn", "type": "submit"}, ["Login"]),
                            ],
                        ),
                    ],
                )
            ],
            title=["Login"],
        )


@dataclasses.dataclass()
class SettingsPage(HeavymetalComponent):
    import_form: ImportForm
    work_count: int
    filename: str

    def heavymetal(self) -> Heavymetal:
        return page(
            [
                section(
                    {},
                    [
                        page_header("Settings", "Manage user data and application data"),
                    ],
                ),
                section(
                    {},
                    [
                        section_header("User data", "This data can only be seen by the current user."),
                        div(
                            {"class": "d-flex flex-column gap-3"},
                            [
                                self.import_box(),
                                self.export_box(),
                                self.clear_box(),
                            ],
                        ),
                    ],
                ),
                section(
                    {},
                    [
                        section_header("Application data", "This data is shared by all users of the application."),
                        self.steam_box(),
                    ],
                ),
            ],
            title=["Settings"],
        )

    def import_box(self) -> Heavymetal:
        disabled = self.work_count > 0

        error_elements = [p({"class": "help is-danger"}, [str(error)]) for error in self.import_form.backup.errors]
        import_button = button({"class": "btn btn-primary", "type": "submit", "disabled": disabled}, ["Import"])

        if self.work_count > 0:
            description = p(
                {"class": "text-danger-emphasis"},
                [f"Import is disabled, you already have {self.work_count} {inf.plural('work', self.work_count)}."],
            )
        else:
            description = p({}, ["Import from a ", code({}, self.filename), " file."])

        return div(
            {"class": "card"},
            [
                div({"class": "card-header"}, "Import data"),
                div(
                    {"class": "card-body"},
                    [
                        description,
                        form(
                            {"action": flask.url_for("user.import"), "method": "POST", "enctype": "multipart/form-data"},
                            [
                                self.import_form.csrf_token(),
                                div(
                                    {"class": "input-group"},
                                    [
                                        self.import_form.backup(disabled=disabled),
                                        import_button,
                                    ],
                                ),
                                *error_elements,
                            ],
                        ),
                    ],
                ),
            ],
        )

    def export_box(self) -> Heavymetal:
        return div(
            {"class": "card"},
            [
                div({"class": "card-header"}, "Export data"),
                div(
                    {"class": "card-body"},
                    [
                        p(
                            {"class": "block"},
                            [
                                f"Export {self.work_count} {inf.plural('work', self.work_count)} to a ",
                                code({}, self.filename),
                                " file.",
                            ],
                        ),
                        a({"href": flask.url_for("user.export"), "class": "btn btn-primary"}, ["Export"]),
                    ],
                ),
            ],
        )

    def clear_box(self) -> Heavymetal:
        command = code({}, [f"flask user clear --username {flask_login.current_user.username}"])

        return div(
            {"class": "card"},
            [
                div({"class": "card-header"}, "Clear data"),
                div(
                    {"class": "card-body"},
                    [
                        p({"class": ""}, ["This is only available from the command line interface."]),
                        p({"class": ""}, [command]),
                    ],
                ),
            ],
        )

    def steam_box(self) -> Heavymetal:
        return div(
            {"class": "card"},
            [
                div({"class": "card-header"}, "Steam AppID list"),
                div(
                    {"class": "card-body"},
                    [
                        p(
                            {},
                            [
                                "Vancelle caches a copy of the Steam AppID list, "
                                "used to search for Steam applications by name."
                            ],
                        ),
                        p(
                            {},
                            [
                                "The list is quite large—expect to wait 30 seconds or so "
                                "for the list to be downloaded and inserted into the database."
                            ],
                        ),
                        form(
                            {"method": "post", "action": flask.url_for(".reload_steam_cache")},
                            [button({"class": "btn btn-warning", "type": "submit"}, ["Reload"])],
                        ),
                    ],
                ),
            ],
        )
