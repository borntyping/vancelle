import flask_wtf
import wtforms.csrf.core
import wtforms.validators

from vancelle.ext.wtforms import NoneFilter


class RecordForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField
    date_started = wtforms.DateField("Started", validators=[wtforms.validators.Optional()])
    date_stopped = wtforms.DateField("Stopped", validators=[wtforms.validators.Optional()])
    date_sync = wtforms.BooleanField("Use start date for end date", default=False)
    notes = wtforms.StringField(
        "Bookmark",
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Length(max=256),
        ],
        filters=[NoneFilter()],
    )
