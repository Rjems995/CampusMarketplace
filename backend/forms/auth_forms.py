"""forms/auth_forms.py — Registration, login, password forms."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from backend.models.user import User


class RegistrationForm(FlaskForm):
    first_name = StringField("First Name",  validators=[DataRequired(), Length(2, 50)])
    last_name  = StringField("Last Name",   validators=[DataRequired(), Length(2, 50)])
    email      = StringField("Email",       validators=[DataRequired(), Email(), Length(max=120)])
    password   = PasswordField("Password",  validators=[DataRequired(), Length(8, 72)])
    confirm    = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])
    submit     = SubmitField("Create Account")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("That email is already registered.")


class LoginForm(FlaskForm):
    email      = StringField("Email",    validators=[DataRequired(), Email()])
    password   = PasswordField("Password", validators=[DataRequired()])
    remember   = BooleanField("Remember me")
    submit     = SubmitField("Log In")


class ForgotPasswordForm(FlaskForm):
    email  = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password",     validators=[DataRequired(), Length(8, 72)])
    confirm  = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit   = SubmitField("Reset Password")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password     = PasswordField("New Password",     validators=[DataRequired(), Length(8, 72)])
    confirm          = PasswordField("Confirm",          validators=[DataRequired(), EqualTo("new_password")])
    submit           = SubmitField("Update Password")
