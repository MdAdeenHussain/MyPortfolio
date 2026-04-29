from datetime import datetime

from models import db


class VisitorEvent(db.Model):
    __tablename__ = "visitor_events"

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(300), nullable=False)
    referrer = db.Column(db.String(600))
    user_agent = db.Column(db.String(600))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))

