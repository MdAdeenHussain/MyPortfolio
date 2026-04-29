from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from extensions import limiter, mail
from models import db
from models.contact import ContactSubmission
from models.visitor import VisitorEvent
from utils.email import send_contact_email

api_bp = Blueprint("api", __name__)


def _client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr


@api_bp.post("/contact")
@limiter.limit("5 per hour")
def contact():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    project = (payload.get("project") or "").strip()
    message = (payload.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify({"success": False, "error": "Missing required fields."}), 400

    submission = ContactSubmission(
        name=name,
        email=email,
        project=project or None,
        message=message,
        ip_address=_client_ip(),
    )

    try:
        db.session.add(submission)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database error."}), 500

    try:
        send_contact_email(
            mail=mail,
            to_email=current_app.config.get("CONTACT_TO_EMAIL"),
            name=name,
            email=email,
            project=project,
            message=message,
        )
    except Exception:
        # Email failures shouldn't block successful form persistence.
        pass

    return jsonify({"success": True})


@api_bp.post("/analytics/visit")
def analytics_visit():
    payload = request.get_json(silent=True) or {}
    path = (payload.get("path") or request.path).strip()
    referrer = (payload.get("referrer") or request.referrer or "").strip()
    user_agent = request.headers.get("User-Agent", "")

    if not path:
        return jsonify({"success": False, "error": "Missing path."}), 400

    event = VisitorEvent(
        path=path[:300],
        referrer=referrer[:600] or None,
        user_agent=(user_agent or "")[:600] or None,
        ip_address=_client_ip(),
    )

    try:
        db.session.add(event)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Database error."}), 500

    return jsonify({"success": True})
