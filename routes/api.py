import os
import re
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from extensions import db, limiter
from models import ActivityLog, ContactLeads, PlanInquiries

api_bp = Blueprint("api", __name__, url_prefix="/api")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_UPLOAD_EXTENSIONS = {"pdf", "doc", "docx", "png", "jpg", "jpeg", "webp"}


def is_valid_email(email):
    return bool(EMAIL_REGEX.match(email or ""))


def get_safe_upload(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError("Unsupported file type")

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    output_name = f"{timestamp}_{filename}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], output_name)
    file_storage.save(upload_path)
    return upload_path


@api_bp.route("/contact", methods=["POST"])
@limiter.limit("10/minute")
def submit_contact():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    company = request.form.get("company", "").strip()
    phone = request.form.get("phone", "").strip()
    selected_plan = request.form.get("selected_plan", "").strip()
    budget = request.form.get("budget", "").strip()
    message = request.form.get("message", "").strip()

    if not full_name or not message:
        return jsonify({"ok": False, "message": "Name and message are required."}), 400
    if not is_valid_email(email):
        return jsonify({"ok": False, "message": "Please enter a valid email."}), 400

    attachment_path = None
    if "attachment" in request.files and request.files["attachment"].filename:
        try:
            attachment_path = get_safe_upload(request.files["attachment"])
        except ValueError as exc:
            return jsonify({"ok": False, "message": str(exc)}), 400

    lead = ContactLeads(
        full_name=full_name,
        email=email,
        company=company,
        phone=phone,
        selected_plan=selected_plan,
        budget=budget,
        message=message,
        attachment_path=attachment_path,
        source="contact-form",
    )
    db.session.add(lead)
    db.session.add(
        ActivityLog(actor_email=email, action="Submitted contact form", entity="ContactLeads", entity_id=0)
    )
    db.session.commit()

    return jsonify({"ok": True, "message": "Thanks, your message has been submitted successfully."})


@api_bp.route("/inquiry", methods=["POST"])
@limiter.limit("15/minute")
def submit_inquiry():
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    service_type = request.form.get("service_type", "").strip()
    plan_name = request.form.get("plan_name", "").strip()
    timeline = request.form.get("timeline", "").strip()
    budget = request.form.get("budget", "").strip()
    project_details = request.form.get("project_details", "").strip()

    if not all([full_name, email, service_type, plan_name, project_details]):
        return jsonify({"ok": False, "message": "Please complete all required fields."}), 400
    if not is_valid_email(email):
        return jsonify({"ok": False, "message": "Please enter a valid email."}), 400

    inquiry = PlanInquiries(
        full_name=full_name,
        email=email,
        service_type=service_type,
        plan_name=plan_name,
        timeline=timeline,
        budget=budget,
        project_details=project_details,
    )
    db.session.add(inquiry)
    db.session.add(
        ActivityLog(actor_email=email, action="Submitted plan inquiry", entity="PlanInquiries", entity_id=0)
    )
    db.session.commit()

    return jsonify({"ok": True, "message": "Inquiry received. I will respond with next steps soon."})
