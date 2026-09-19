from datetime import datetime, date
from app import db


class Scholarship(db.Model):
    """A single scholarship application record."""

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    organization = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    due_date = db.Column(db.Date, nullable=False)

    # Stored as a plain string with a fixed set of allowed values enforced
    # in the form layer (forms.py), rather than a native DB enum. This
    # keeps SQLite (which has no real enum type) and Postgres consistent,
    # and makes new statuses a one-line change instead of a migration.
    status = db.Column(db.String(20), nullable=False, default="not_started")

    notes = db.Column(db.Text, nullable=True)
    application_link = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # The allowed status values, defined once here so forms.py and any
    # future code (like the Gmail matcher in Phase 4) share one source
    # of truth instead of duplicating this list.
    STATUSES = ["not_started", "in_progress", "submitted", "awarded", "rejected"]

    def __repr__(self):
        return f"<Scholarship {self.id} {self.name!r} ({self.status})>"

    @property
    def is_overdue(self):
        """True if the due date has passed and nothing was ever submitted."""
        return self.due_date < date.today() and self.status in ("not_started", "in_progress")