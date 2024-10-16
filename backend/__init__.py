"""Main backend package."""

from flask_cors import CORS
import logging
import sys
from flask import Flask
from backend import routes

from backend.models.course import Course
from backend.models.coursesection import CourseSection
from backend.models.registrationqueue import RegistrationQueue
from backend.models.schedule import Schedule
from backend.models.user import User

from backend.extensions import bcrypt, db, migrate

from backend.routes import user as user_routes

def create_backend():
    app = Flask(__name__).split(".")[0]
    app.config.from_pyfile('../.env', silent=True)
    register_extensions(app)
    register_blueprints(app)
    configure_logger(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    return app


def register_extensions(app):
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    return None

def register_requestwrapper(app):
    return None

def register_blueprints(app):
    """Register blueprints."""
    app.register_blueprint(user_routes.bp, url_prefix='/api/user')
    return None

def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
