import itertools

import flask_wtf
import wtforms.csrf.core
import wtforms.validators

from vancelle.ext.wtforms import NoneFilter
from vancelle.models.remote import Remote
from vancelle.models.work import Work, Book
from vancelle.shelf import Case, Shelf

SHELF_FORM_CHOICES = {
    group: [(shelf.value, shelf.title) for shelf in items]
    for group, items in itertools.groupby(Shelf, key=lambda shelf: shelf.group)
}

TYPE_FORM_CHOICES = [(cls.work_type(), cls.info.noun_title) for cls in Work.iter_subclasses()]


class ShelveWorkForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField

    shelf = wtforms.SelectField(
        "Shelf",
        choices=SHELF_FORM_CHOICES,
        coerce=Shelf,
        default=Shelf.UNSORTED,
        validators=[wtforms.validators.DataRequired()],
    )


class WorkForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField

    type = wtforms.SelectField("Type", choices=TYPE_FORM_CHOICES, default=Book.polymorphic_identity())
    shelf = wtforms.SelectField("Shelf", coerce=Shelf, choices=SHELF_FORM_CHOICES, default=Shelf.UNSORTED)

    # Details
    title = wtforms.StringField("Title", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    author = wtforms.StringField("Author", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    series = wtforms.StringField("Series", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    release_date = wtforms.DateField("Release Date", validators=[wtforms.validators.Optional()])
    description = wtforms.TextAreaField("Description", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    cover = wtforms.URLField("Cover image", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    background = wtforms.URLField("Background image", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    # tags = wtforms.StringField('tags')

    # Properties
    external_url = wtforms.URLField("External URL", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])
    isbn = wtforms.StringField("ISBN", validators=[wtforms.validators.Optional()], filters=[NoneFilter()])


class WorkIndexForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField

    layout = wtforms.SelectField(
        label="Layout",
        choices=[
            ("vertical", "Vertical"),
            ("horizontal", "Horizontal"),
            ("board", "Board"),
            ("list", "List"),
        ],
        default="vertical",
        validators=[wtforms.validators.DataRequired()],
    )
    work_type = wtforms.SelectField(
        label="Work type",
        choices=[("", "All works")] + [(cls.work_type(), cls.info.noun_plural_title) for cls in Work.iter_subclasses()],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    work_shelf = wtforms.SelectField(
        label="Exact shelf",
        coerce=lambda x: Shelf(x) if x else None,
        choices=[("", "All shelves")] + [(s.value, s.title) for s in Shelf],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    work_case = wtforms.SelectField(
        label="Shelves",
        coerce=lambda x: Case(x) if x else None,
        choices=[("", "All shelves")] + [(g.value, g.title) for g in Case],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    work_deleted = wtforms.SelectField(
        label="Deleted works",
        choices=[
            ("no", "Don't include deleted works"),
            ("all", "Include deleted works"),
            ("yes", "Only deleted works"),
        ],
        default="no",
        validators=[wtforms.validators.DataRequired()],
    )

    remote_type = wtforms.SelectField(
        label="Remote type",
        choices=[("", "All remote types")] + [(cls.remote_type(), cls.info.noun_full) for cls in Remote.iter_subclasses()],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    remote_data = wtforms.SelectField(
        label="Has remote",
        choices=[
            ("", "Any remote data"),
            ("yes", "Has remote data"),
            ("imported", "Only imported data"),
            ("no", "No remote data"),
        ],
        default="",
        validators=[wtforms.validators.Optional()],
    )
    search = wtforms.SearchField(label="Query", validators=[wtforms.validators.Optional()])
