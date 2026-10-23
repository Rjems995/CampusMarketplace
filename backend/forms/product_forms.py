"""forms/product_forms.py — Listing create/edit form."""

from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


CONDITIONS = [("", "Select condition…"), ("New","New"), ("Like New","Like New"), ("Good","Good"), ("Fair","Fair"), ("Poor","Poor")]


class ProductForm(FlaskForm):
    title       = StringField("Title",       validators=[DataRequired(), Length(3, 150)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(10, 5000)])
    price       = DecimalField("Price (₱)", validators=[DataRequired(), NumberRange(min=0)], places=2)
    condition   = SelectField("Condition",  choices=CONDITIONS, validators=[DataRequired()])
    category_id = SelectField("Category",   coerce=int, validators=[DataRequired()])
    location    = StringField("Location",   validators=[Optional(), Length(max=100)])
    images      = MultipleFileField("Photos", validators=[
        FileAllowed(["jpg","jpeg","png","gif","webp"], "Images only!")
    ])
    submit = SubmitField("Save Listing")
