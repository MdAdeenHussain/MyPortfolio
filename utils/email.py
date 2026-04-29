from flask_mail import Message


def send_contact_email(*, mail, to_email, name, email, project, message):
    if not to_email:
        return

    subject = "New Portfolio Contact Submission"
    project_line = project.strip() if project else ""
    body = "\n".join(
        [
            "New contact submission:",
            "",
            f"Name: {name}",
            f"Email: {email}",
            f"Project: {project_line}",
            "",
            "Message:",
            message,
        ]
    )

    msg = Message(subject=subject, recipients=[to_email], body=body)
    mail.send(msg)

