from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models for Alembic autogenerate discovery.
from models.contact import ContactSubmission  # noqa: E402,F401
from models.visitor import VisitorEvent  # noqa: E402,F401
