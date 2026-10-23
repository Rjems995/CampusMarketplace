"""forms/profile_forms.py — Profile edit and review forms."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import Optional, Length, NumberRange, URL


YEAR_LEVELS = [("", "Select year…"), ("1st Year","1st Year"), ("2nd Year","2nd Year"),
               ("3rd Year","3rd Year"), ("4th Year","4th Year"), ("5th Year","5th Year"), ("Graduate","Graduate")]


class ProfileEditForm(FlaskForm):
    first_name      = StringField("First Name", validators=[Length(2, 50)])
    last_name       = StringField("Last Name",  validators=[Length(2, 50)])
    bio             = TextAreaField("Bio",       validators=[Optional(), Length(max=500)])
    course          = StringField("Course / Program", validators=[Optional(), Length(max=100)])
    year_level      = SelectField("Year Level", choices=YEAR_LEVELS, validators=[Optional()])
    school          = StringField("School / University", validators=[Optional(), Length(max=150)])
    phone           = StringField("Phone Number",        validators=[Optional(), Length(max=20)])
    location        = StringField("Location",            validators=[Optional(), Length(max=100)])
    social_fb       = StringField("Facebook Profile URL",validators=[Optional(), URL(), Length(max=255)])
    profile_picture = FileField("Profile Picture", validators=[FileAllowed(["jpg","jpeg","png","webp"])])
    submit          = SubmitField("Save Changes")


class ReviewForm(FlaskForm):
    rating  = IntegerField("Rating", validators=[NumberRange(min=1, max=5)])
    comment = TextAreaField("Comment", validators=[Optional(), Length(max=1000)])
    submit  = SubmitField("Submit Review")


class ReportForm(FlaskForm):
    reason      = SelectField("Reason", choices=[r for r in [
        ("fake_listing","Fake Listing"), ("spam","Spam"), ("scam","Scam / Fraud"),
        ("offensive_content","Offensive Content"), ("duplicate","Duplicate Listing"),
        ("wrong_category","Wrong Category"), ("other","Other"),
    ]])
    description = TextAreaField("Details", validators=[Optional(), Length(max=1000)])
    submit      = SubmitField("Submit Report")
