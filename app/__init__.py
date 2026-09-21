import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from config import config_by_name

# Extensions are created here, unattached to any app, then bound
# inside create_app(). This is what makes the app factory pattern work:
# multiple app instances (dev, testing) can each get their own config
# without these extensions being tied to a single global app.
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_name=None):
    """Application factory: builds and returns a configured Flask app."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Ensure the instance folder (holds the SQLite file) exists.
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "main.login"
    @login_manager.user_loader
    def load_user(user_id):
        # Placeholder until Phase 3 builds real User accounts.
        # Returning None means Flask-Login always treats requests as
        # "not logged in" for now, which is fine since nothing is
        # protected with @login_required yet.
        return None
    from app import models  # noqa: F401  (import so SQLAlchemy sees the models)
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    return app