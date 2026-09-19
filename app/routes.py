from flask import Blueprint

# Blueprints let you organize routes into modules and register them on the
# app inside create_app(). Right now everything lives in one blueprint
# ("main"); if the app grows, you could split auth routes, API routes, etc.
# into their own blueprints later without restructuring what's here.
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return "Scholarship Tracker skeleton is running."