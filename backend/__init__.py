"""Main backend package."""
from flask_cors import CORS
import logging
import sys
import os
from flask import Flask
from backend.extensions import bcrypt, db, migrate, mail

def create_backend():
    app = Flask(__name__.split(".")[0])
    app.config.from_pyfile('../.env', silent=True)
    
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    register_extensions(app)
    register_blueprints(app)
    configure_logger(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    return app

def register_extensions(app):
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    return None

def register_blueprints(app):
    from backend.routes import user as user_routes
    from backend.routes import queue as queue_routes
    app.register_blueprint(user_routes.bp, url_prefix='/api/user')
    app.register_blueprint(queue_routes.bp, url_prefix='/api/queue')
    return None

def configure_logger(app):
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
