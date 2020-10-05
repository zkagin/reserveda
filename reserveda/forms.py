# forms.py
# Contains all UI-based forms and their validation logic.

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, ValidationError, Length, Email
from reserveda.models import User


class SignUpForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(message="Please use a valid email address.")],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(
                min=8,
                message="Please use a password that is at least 8 characters long.",
            ),
        ],
    )
    code = StringField("Group Code (optional)")
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("That address is already in use.")


class LogInForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class AddItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Add")
