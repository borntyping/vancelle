import wtforms.csrf.core
import flask_wtf.file
import wtforms

from vancelle.html.bootstrap.forms.controls import BootstrapFileInput


class LoginForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField

    username = wtforms.StringField("Username")
    password = wtforms.PasswordField("Password")


class ImportForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField

    backup = flask_wtf.file.FileField(
        "Backup",
        widget=BootstrapFileInput(),
        validators=[flask_wtf.file.FileRequired()],
    )
