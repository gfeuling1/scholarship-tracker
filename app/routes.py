from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Scholarship
from app.forms import ScholarshipForm

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """List scholarships, optionally filtered by status and/or search text."""
    status_filter = request.args.get("status", "")
    search_query = request.args.get("q", "").strip()

    query = Scholarship.query

    if status_filter:
        query = query.filter(Scholarship.status == status_filter)

    if search_query:
        # ilike = case-insensitive LIKE. The %...% wildcards mean "contains",
        # not "starts with" or "exact match".
        query = query.filter(
            db.or_(
                Scholarship.name.ilike(f"%{search_query}%"),
                Scholarship.organization.ilike(f"%{search_query}%"),
            )
        )

    scholarships = query.order_by(Scholarship.due_date.asc()).all()

    return render_template(
        "index.html",
        scholarships=scholarships,
        statuses=Scholarship.STATUSES,
        status_filter=status_filter,
        search_query=search_query,
    )

@main_bp.route("/dashboard")
def dashboard():
    """Summary view: upcoming deadlines and totals."""
    from datetime import date

    all_scholarships = Scholarship.query.all()

    # Upcoming = not yet resolved (still worth tracking a deadline for)
    # and due today or later, soonest first.
    upcoming = sorted(
        [s for s in all_scholarships if s.status in ("not_started", "in_progress", "submitted") and s.due_date >= date.today()],
        key=lambda s: s.due_date,
    )

    # "Applied for" = money tied up in anything you've actually submitted
    # or are working on — not started doesn't count yet.
    total_applied = sum(
        s.amount for s in all_scholarships if s.status in ("in_progress", "submitted")
    )
    total_awarded = sum(s.amount for s in all_scholarships if s.status == "awarded")
    total_potential = sum(s.amount for s in all_scholarships if s.status != "rejected")

    # Build {status: total_amount} for every status, in a fixed order,
    # so the chart's bars always appear in the same left-to-right sequence
    # regardless of which statuses happen to have data.
    amounts_by_status = {
        status: sum(s.amount for s in all_scholarships if s.status == status)
        for status in Scholarship.STATUSES
    }

    return render_template(
        "dashboard.html",
        upcoming=upcoming,
        total_applied=total_applied,
        total_awarded=total_awarded,
        total_potential=total_potential,
        amounts_by_status=amounts_by_status,
    )

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