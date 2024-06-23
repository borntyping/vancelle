from vancelle.forms.record import RecordForm
from vancelle.html.bootstrap.forms.controls import form_control, form_control_check
from vancelle.html.bootstrap.layout.grid import col, row
from vancelle.html.vancelle.components.header import PageHeader
from vancelle.html.vancelle.pages.base import Page
from vancelle.html.vancelle.components.work import return_to_work
from vancelle.lib.heavymetal import Heavymetal, HeavymetalContent
from vancelle.lib.heavymetal.html import button, div, form
from vancelle.models import Record


def _record_controls(record: Record) -> HeavymetalContent:
    if record.deleted:
        yield button(
            {
                "class": "btn btn-outline-danger",
                "type": "submit",
                "formmethod": "post",
                "formaction": record.url_for_permanently_delete(),
                "title": "Delete this record. It will not be possible to recover.",
            },
            ["Permanently delete"],
        )
        yield button(
            {
                "class": "btn btn-outline-success",
                "type": "submit",
                "formmethod": "post",
                "formaction": record.url_for_restore(),
                "title": "Restore this record.",
            },
            ["Restore"],
        )
    else:
        yield button(
            {
                "class": "btn btn-outline-primary",
                "type": "submit",
                "formmethod": "post",
                "formaction": record.url_for_delete(),
                "title": "Delete this record. You will be able to restore it.",
            },
            ["Delete"],
        )


def record_update_page(record: Record, record_form: RecordForm) -> Heavymetal:
    title = record.work.resolve_title()
    return Page(
        [
            PageHeader(
                "Edit record",
                return_to_work(record.work),
                form({"class": "btn-toolbar"}, [div({"class": "btn-group"}, [*_record_controls(record)])]),
            ),
            form(
                {"method": "post", "action": record.url_for()},
                [
                    record_form.csrf_token,
                    row(
                        {"class": "mb-3"},
                        [
                            col({}, [form_control(record_form.date_started)]),
                            col({}, [form_control(record_form.date_stopped)]),
                        ],
                    ),
                    row(
                        {"class": "mb-3"},
                        [
                            col(
                                {},
                                [
                                    form_control(
                                        record_form.notes,
                                        rows=5,
                                        cols=20,
                                        autocomplete="off",
                                        autocorrect="on",
                                        maxlength="256",
                                    )
                                ],
                            ),
                        ],
                    ),
                    row(
                        {"class": "mt-4"},
                        [
                            col(
                                {"class": "d-flex justify-content-start align-items-center gap-3"},
                                [
                                    button({"class": "btn btn-primary", "type": "submit"}, ["Save changes"]),
                                    form_control_check(record_form.date_sync, switch=True),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
        title=[title, "Update record"],
    )
