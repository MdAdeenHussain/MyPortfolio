from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os

from config import Config
from extensions import limiter, mail
from models import db
from routes.api import api_bp
from routes.main import main_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    uri = str(app.config.get("SQLALCHEMY_DATABASE_URI", ""))
    if uri.startswith("postgresql"):
        try:
            engine = create_engine(uri)
            with engine.connect():
                pass
        except OperationalError:
            sqlite_path = os.path.join(app.instance_path, "portfolio.db")
            os.makedirs(app.instance_path, exist_ok=True)
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
            uri = app.config["SQLALCHEMY_DATABASE_URI"]

    if uri.startswith("sqlite:///"):
        os.makedirs(app.instance_path, exist_ok=True)
        # If a relative sqlite path is used, rewrite it to the Flask instance folder.
        if "/instance/" in uri:
            sqlite_path = os.path.join(app.instance_path, "portfolio.db")
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
            uri = app.config["SQLALCHEMY_DATABASE_URI"]

    db.init_app(app)
    Migrate(app, db)

    mail.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    if str(app.config.get("SQLALCHEMY_DATABASE_URI", "")).startswith("sqlite"):
        with app.app_context():
            db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
