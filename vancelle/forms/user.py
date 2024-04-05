import wtforms.csrf.core
import flask_wtf.file
import wtforms


class LoginForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField

    username = wtforms.StringField("Username")
    password = wtforms.PasswordField("Password")


class ImportForm(flask_wtf.FlaskForm):
    csrf_token: wtforms.csrf.core.CSRFTokenField

    backup = flask_wtf.file.FileField("Backup", validators=[flask_wtf.file.FileRequired()])
