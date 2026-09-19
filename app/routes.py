from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Scholarship
from app.forms import ScholarshipForm

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """List all scholarships, sorted by soonest due date first."""
    scholarships = Scholarship.query.order_by(Scholarship.due_date.asc()).all()
    return render_template("index.html", scholarships=scholarships)


@main_bp.route("/scholarships/new", methods=["GET", "POST"])
def create_scholarship():
    """Show the create form (GET) or save a new scholarship (POST)."""
    form = ScholarshipForm()

    if form.validate_on_submit():
        scholarship = Scholarship(
            name=form.name.data,
            organization=form.organization.data,
            amount=form.amount.data,
            due_date=form.due_date.data,
            status=form.status.data,
            notes=form.notes.data,
            application_link=form.application_link.data,
        )
        db.session.add(scholarship)
        db.session.commit()
        flash(f'Added "{scholarship.name}".', "success")
        return redirect(url_for("main.index"))

    # If we get here on a POST, validation failed — form.errors will
    # have the details, and the template will display them.
    return render_template("scholarship_form.html", form=form, title="Add Scholarship")


@main_bp.route("/scholarships/<int:scholarship_id>/edit", methods=["GET", "POST"])
def edit_scholarship(scholarship_id):
    """Show the edit form (GET) or save changes (POST)."""
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    form = ScholarshipForm(obj=scholarship)

    if form.validate_on_submit():
        scholarship.name = form.name.data
        scholarship.organization = form.organization.data
        scholarship.amount = form.amount.data
        scholarship.due_date = form.due_date.data
        scholarship.status = form.status.data
        scholarship.notes = form.notes.data
        scholarship.application_link = form.application_link.data
        db.session.commit()
        flash(f'Updated "{scholarship.name}".', "success")
        return redirect(url_for("main.index"))

    return render_template("scholarship_form.html", form=form, title="Edit Scholarship")


@main_bp.route("/scholarships/<int:scholarship_id>/delete", methods=["POST"])
def delete_scholarship(scholarship_id):
    """Delete a scholarship. POST-only so it can't happen from a GET link/crawler."""
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    db.session.delete(scholarship)
    db.session.commit()
    flash(f'Deleted "{scholarship.name}".', "success")
    return redirect(url_for("main.index"))