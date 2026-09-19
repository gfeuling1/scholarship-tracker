from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, URL, Optional, Length

from app.models import Scholarship


class ScholarshipForm(FlaskForm):
    """Validates input for both creating and editing a scholarship."""

    name = StringField(
        "Scholarship Name",
        validators=[DataRequired(), Length(max=200)],
    )
    organization = StringField(
        "Organization",
        validators=[DataRequired(), Length(max=200)],
    )
    amount = FloatField(
        "Amount ($)",
        validators=[DataRequired(), NumberRange(min=0, message="Amount can't be negative.")],
    )
    due_date = DateField(
        "Due Date",
        validators=[DataRequired()],
    )
    status = SelectField(
        "Status",
        # Built from Scholarship.STATUSES instead of hardcoded here, so
        # adding a new status only ever requires touching the model.
        choices=[(s, s.replace("_", " ").title()) for s in Scholarship.STATUSES],
        validators=[DataRequired()],
    )
    notes = TextAreaField(
        "Requirements / Notes",
        validators=[Optional(), Length(max=2000)],
    )
    application_link = StringField(
        "Application Link",
        validators=[Optional(), URL(message="Enter a valid URL, e.g. https://..."), Length(max=500)],
    )