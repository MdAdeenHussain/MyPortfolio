import csv
import io
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_

from extensions import db, limiter
from models import (
    ActivityLog,
    AdminUser,
    AutomationLogs,
    BlogPosts,
    ContactLeads,
    NotificationAlert,
    Payments,
    PlanCatalog,
    PlanInquiries,
    PortfolioProjects,
    SiteSettings,
    Testimonials,
    slugify,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def log_action(action, entity, entity_id=0):
    actor = current_user.email if current_user.is_authenticated else "system"
    db.session.add(ActivityLog(actor_email=actor, action=action, entity=entity, entity_id=entity_id))


def build_unique_slug(model, base_value, fallback):
    base_slug = slugify(base_value) if base_value else slugify(fallback)
    slug = base_slug
    i = 2
    while model.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{i}"
        i += 1
    return slug


def subtract_months(source_date, months_back):
    year = source_date.year
    month = source_date.month - months_back
    while month <= 0:
        month += 12
        year -= 1
    return source_date.replace(year=year, month=month, day=1)


def normalize_url(raw_url):
    value = (raw_url or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value
    return f"https://{value}"


def get_or_create_site_settings():
    settings = SiteSettings.query.first()
    if settings:
        return settings
    settings = SiteSettings(whatsapp_number="+91 9674667587")
    db.session.add(settings)
    db.session.flush()
    return settings


def admin_only_required():
    if not current_user.is_authenticated:
        return redirect(url_for("admin.login"))
    if current_user.role not in {"admin", "editor"}:
        flash("Access denied.", "danger")
        return redirect(url_for("admin.dashboard"))
    return None


def parse_iso_date(raw_value):
    value = (raw_value or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def build_past_clients_rows(search_query="", source_filter=""):
    q = (search_query or "").strip().lower()
    source_filter = (source_filter or "").strip().lower()

    lead_query = ContactLeads.query.filter(ContactLeads.status.in_(["done", "closed"]))
    inquiry_query = PlanInquiries.query.filter(PlanInquiries.status == "done")

    if q:
        like_pattern = f"%{q}%"
        lead_query = lead_query.filter(
            or_(
                ContactLeads.full_name.ilike(like_pattern),
                ContactLeads.email.ilike(like_pattern),
                ContactLeads.company.ilike(like_pattern),
                ContactLeads.selected_plan.ilike(like_pattern),
            )
        )
        inquiry_query = inquiry_query.filter(
            or_(
                PlanInquiries.full_name.ilike(like_pattern),
                PlanInquiries.email.ilike(like_pattern),
                PlanInquiries.plan_name.ilike(like_pattern),
                PlanInquiries.service_type.ilike(like_pattern),
            )
        )

    rows = []
    if source_filter in {"", "contacted"}:
        for lead in lead_query.all():
            rows.append(
                {
                    "name": lead.full_name,
                    "email": lead.email,
                    "source": "contacted",
                    "service": lead.selected_plan or "-",
                    "status": lead.status or "done",
                    "maintenance_subscribed": bool(lead.maintenance_subscribed),
                    "maintenance_until": lead.maintenance_until,
                    "completed_at": lead.completed_at or lead.updated_at or lead.created_at,
                }
            )

    if source_filter in {"", "inquired"}:
        for inquiry in inquiry_query.all():
            rows.append(
                {
                    "name": inquiry.full_name,
                    "email": inquiry.email,
                    "source": "inquired",
                    "service": f"{inquiry.service_type} - {inquiry.plan_name}",
                    "status": inquiry.status or "done",
                    "maintenance_subscribed": bool(inquiry.maintenance_subscribed),
                    "maintenance_until": inquiry.maintenance_until,
                    "completed_at": inquiry.completed_at or inquiry.updated_at or inquiry.created_at,
                }
            )

    rows.sort(key=lambda row: row["completed_at"] or datetime.min, reverse=True)
    return rows


@admin_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10/minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = AdminUser.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash("Welcome back.", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Invalid credentials.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("admin.login"))


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    gate = admin_only_required()
    if gate:
        return gate

    total_leads = ContactLeads.query.count()
    active_projects = PortfolioProjects.query.count()
    monthly_revenue = db.session.query(func.coalesce(func.sum(Payments.amount), 0)).scalar() or 0
    pending_inquiries = PlanInquiries.query.filter_by(status="pending").count()

    health_status = "Healthy"
    recent_logs = AutomationLogs.query.order_by(AutomationLogs.created_at.desc()).limit(5).all()
    if any(log.status.lower() in {"warning", "error", "failed"} for log in recent_logs):
        health_status = "Needs Attention"

    months = []
    lead_points = []
    revenue_points = []
    now = datetime.utcnow().replace(day=1)
    for i in range(5, -1, -1):
        month_start = subtract_months(now, i)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        month_label = month_start.strftime("%b")
        leads_count = (
            ContactLeads.query.filter(ContactLeads.created_at >= month_start, ContactLeads.created_at < month_end).count()
        )
        rev_sum = (
            db.session.query(func.coalesce(func.sum(Payments.amount), 0))
            .filter(Payments.created_at >= month_start, Payments.created_at < month_end)
            .scalar()
        )
        months.append(month_label)
        lead_points.append(leads_count)
        revenue_points.append(float(rev_sum or 0))

    distribution_raw = (
        db.session.query(PlanInquiries.plan_name, func.count(PlanInquiries.id))
        .group_by(PlanInquiries.plan_name)
        .all()
    )
    dist_labels = [row[0] for row in distribution_raw] or ["No Data"]
    dist_values = [row[1] for row in distribution_raw] or [1]

    service_raw = (
        db.session.query(PlanInquiries.service_type, func.count(PlanInquiries.id))
        .group_by(PlanInquiries.service_type)
        .all()
    )
    service_labels = [row[0] for row in service_raw] or ["No Data"]
    service_values = [row[1] for row in service_raw] or [1]

    traffic_data = {
        "labels": ["Direct", "Search", "Referral", "Social", "Email"],
        "values": [32, 29, 18, 15, 6],
    }

    alerts = NotificationAlert.query.order_by(NotificationAlert.created_at.desc()).limit(6).all()
    activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(12).all()

    return render_template(
        "admin/dashboard.html",
        metrics={
            "total_leads": total_leads,
            "active_projects": active_projects,
            "monthly_revenue": monthly_revenue,
            "pending_inquiries": pending_inquiries,
            "health_status": health_status,
        },
        chart_data={
            "months": months,
            "lead_points": lead_points,
            "revenue_points": revenue_points,
            "dist_labels": dist_labels,
            "dist_values": dist_values,
            "service_labels": service_labels,
            "service_values": service_values,
            "traffic": traffic_data,
        },
        alerts=alerts,
        activities=activities,
    )


@admin_bp.route("/leads")
@login_required
def leads():
    gate = admin_only_required()
    if gate:
        return gate

    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()

    query = ContactLeads.query
    if q:
        like_pattern = f"%{q}%"
        query = query.filter(
            or_(
                ContactLeads.full_name.ilike(like_pattern),
                ContactLeads.email.ilike(like_pattern),
                ContactLeads.company.ilike(like_pattern),
                ContactLeads.selected_plan.ilike(like_pattern),
            )
        )
    if status:
        query = query.filter_by(status=status)

    rows = query.order_by(ContactLeads.created_at.desc()).all()
    return render_template("admin/leads.html", leads=rows, q=q, status=status)


@admin_bp.route("/leads/<int:lead_id>/update", methods=["POST"])
@login_required
def update_lead(lead_id):
    gate = admin_only_required()
    if gate:
        return gate

    row = ContactLeads.query.get_or_404(lead_id)
    next_status = request.form.get("status", "").strip().lower()
    allowed_status = {"new", "contacted", "qualified", "accepted", "rejected", "done", "closed"}
    if next_status not in allowed_status:
        flash("Invalid lead status.", "danger")
        return redirect(url_for("admin.leads"))

    maintenance_subscribed = request.form.get("maintenance_subscribed") == "on"
    maintenance_until = parse_iso_date(request.form.get("maintenance_until", ""))
    maintenance_until_raw = request.form.get("maintenance_until", "").strip()
    if maintenance_until_raw and not maintenance_until:
        flash("Invalid maintenance end date.", "danger")
        return redirect(url_for("admin.leads"))

    if next_status not in {"done", "closed"}:
        maintenance_subscribed = False
        maintenance_until = None
        row.completed_at = None
    else:
        row.completed_at = datetime.utcnow()
        if maintenance_subscribed and not maintenance_until:
            flash("Please add maintenance end date when subscription is active.", "danger")
            return redirect(url_for("admin.leads"))
        if not maintenance_subscribed:
            maintenance_until = None

    row.status = next_status
    row.maintenance_subscribed = maintenance_subscribed
    row.maintenance_until = maintenance_until
    log_action("Updated lead workflow", "ContactLeads", row.id)
    db.session.commit()
    flash("Lead updated.", "success")
    return redirect(url_for("admin.leads"))


@admin_bp.route("/leads/export")
@login_required
def export_leads_csv():
    gate = admin_only_required()
    if gate:
        return gate

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "Name",
            "Email",
            "Company",
            "Plan",
            "Budget",
            "Status",
            "Maintenance Subscribed",
            "Maintenance Until",
            "Completed At",
            "Created At",
        ]
    )

    for lead in ContactLeads.query.order_by(ContactLeads.created_at.desc()).all():
        writer.writerow(
            [
                lead.id,
                lead.full_name,
                lead.email,
                lead.company,
                lead.selected_plan,
                lead.budget,
                lead.status,
                "Yes" if lead.maintenance_subscribed else "No",
                lead.maintenance_until.strftime("%Y-%m-%d") if lead.maintenance_until else "",
                lead.completed_at.strftime("%Y-%m-%d %H:%M") if lead.completed_at else "",
                lead.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=contact_leads.csv"
    return response


@admin_bp.route("/leads/<int:lead_id>/delete", methods=["POST"])
@login_required
def delete_lead(lead_id):
    gate = admin_only_required()
    if gate:
        return gate

    row = ContactLeads.query.get_or_404(lead_id)
    db.session.delete(row)
    log_action("Deleted lead", "ContactLeads", lead_id)
    db.session.commit()
    flash("Lead deleted.", "success")
    return redirect(url_for("admin.leads"))


@admin_bp.route("/inquiries")
@login_required
def inquiries():
    gate = admin_only_required()
    if gate:
        return gate

    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()

    query = PlanInquiries.query
    if q:
        like_pattern = f"%{q}%"
        query = query.filter(
            or_(
                PlanInquiries.full_name.ilike(like_pattern),
                PlanInquiries.email.ilike(like_pattern),
                PlanInquiries.plan_name.ilike(like_pattern),
                PlanInquiries.service_type.ilike(like_pattern),
            )
        )
    if status:
        query = query.filter_by(status=status)

    rows = query.order_by(PlanInquiries.created_at.desc()).all()
    return render_template("admin/inquiries.html", inquiries=rows, q=q, status=status)


@admin_bp.route("/inquiries/export")
@login_required
def export_inquiries_csv():
    gate = admin_only_required()
    if gate:
        return gate

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "Name",
            "Email",
            "Service Type",
            "Plan Name",
            "Timeline",
            "Budget",
            "Status",
            "Maintenance Subscribed",
            "Maintenance Until",
            "Completed At",
            "Created At",
        ]
    )

    for row in PlanInquiries.query.order_by(PlanInquiries.created_at.desc()).all():
        writer.writerow(
            [
                row.id,
                row.full_name,
                row.email,
                row.service_type,
                row.plan_name,
                row.timeline or "",
                row.budget or "",
                row.status,
                "Yes" if row.maintenance_subscribed else "No",
                row.maintenance_until.strftime("%Y-%m-%d") if row.maintenance_until else "",
                row.completed_at.strftime("%Y-%m-%d %H:%M") if row.completed_at else "",
                row.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=plan_inquiries.csv"
    return response


@admin_bp.route("/inquiries/<int:inquiry_id>/update", methods=["POST"])
@login_required
def update_inquiry(inquiry_id):
    gate = admin_only_required()
    if gate:
        return gate

    row = PlanInquiries.query.get_or_404(inquiry_id)
    next_status = request.form.get("status", "").strip().lower()
    allowed_status = {"pending", "accepted", "rejected", "done"}
    if next_status not in allowed_status:
        flash("Invalid inquiry status.", "danger")
        return redirect(url_for("admin.inquiries"))

    maintenance_subscribed = request.form.get("maintenance_subscribed") == "on"
    maintenance_until_raw = request.form.get("maintenance_until", "").strip()
    maintenance_until = parse_iso_date(maintenance_until_raw)
    if maintenance_until_raw and not maintenance_until:
        flash("Invalid maintenance end date.", "danger")
        return redirect(url_for("admin.inquiries"))

    if next_status != "done":
        maintenance_subscribed = False
        maintenance_until = None
        row.completed_at = None
    else:
        row.completed_at = datetime.utcnow()
        if maintenance_subscribed and not maintenance_until:
            flash("Please add maintenance end date when subscription is active.", "danger")
            return redirect(url_for("admin.inquiries"))
        if not maintenance_subscribed:
            maintenance_until = None

    row.status = next_status
    row.maintenance_subscribed = maintenance_subscribed
    row.maintenance_until = maintenance_until
    log_action("Updated inquiry workflow", "PlanInquiries", row.id)
    db.session.commit()
    flash("Inquiry updated.", "success")
    return redirect(url_for("admin.inquiries"))


@admin_bp.route("/past-clients")
@login_required
def past_clients():
    gate = admin_only_required()
    if gate:
        return gate

    q = request.args.get("q", "").strip()
    source = request.args.get("source", "").strip().lower()
    rows = build_past_clients_rows(q, source)
    return render_template("admin/past_clients.html", clients=rows, q=q, source=source)


@admin_bp.route("/past-clients/export")
@login_required
def export_past_clients_csv():
    gate = admin_only_required()
    if gate:
        return gate

    q = request.args.get("q", "").strip()
    source = request.args.get("source", "").strip().lower()
    rows = build_past_clients_rows(q, source)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Name",
            "Email",
            "Source",
            "Service/Plan",
            "Status",
            "Maintenance Subscribed",
            "Maintenance Until",
            "Completed At",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["name"],
                row["email"],
                row["source"],
                row["service"],
                row["status"],
                "Yes" if row["maintenance_subscribed"] else "No",
                row["maintenance_until"].strftime("%Y-%m-%d") if row["maintenance_until"] else "",
                row["completed_at"].strftime("%Y-%m-%d %H:%M") if row["completed_at"] else "",
            ]
        )

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=past_clients.csv"
    return response


@admin_bp.route("/inquiries/<int:inquiry_id>/delete", methods=["POST"])
@login_required
def delete_inquiry(inquiry_id):
    gate = admin_only_required()
    if gate:
        return gate

    row = PlanInquiries.query.get_or_404(inquiry_id)
    db.session.delete(row)
    log_action("Deleted inquiry", "PlanInquiries", inquiry_id)
    db.session.commit()
    flash("Inquiry deleted.", "success")
    return redirect(url_for("admin.inquiries"))


@admin_bp.route("/blogs", methods=["GET", "POST"])
@login_required
def blogs():
    gate = admin_only_required()
    if gate:
        return gate

    edit_id = request.args.get("edit", type=int)
    blog_to_edit = BlogPosts.query.get(edit_id) if edit_id else None

    if request.method == "POST":
        form_id = request.form.get("id", type=int)
        title = request.form.get("title", "").strip()
        excerpt = request.form.get("excerpt", "").strip()
        content = request.form.get("content", "").strip()
        tags = request.form.get("tags", "").strip()
        is_published = request.form.get("is_published") == "on"

        if not all([title, excerpt, content]):
            flash("Title, excerpt, and content are required.", "danger")
            return redirect(url_for("admin.blogs"))

        if form_id:
            post = BlogPosts.query.get_or_404(form_id)
            post.title = title
            post.excerpt = excerpt
            post.content = content
            post.tags = tags
            post.is_published = is_published
            if not post.slug:
                post.slug = build_unique_slug(BlogPosts, title, "blog")
            log_action("Updated blog post", "BlogPosts", post.id)
            flash("Blog post updated.", "success")
        else:
            post = BlogPosts(
                title=title,
                slug=build_unique_slug(BlogPosts, title, "blog"),
                excerpt=excerpt,
                content=content,
                tags=tags,
                is_published=is_published,
                author_id=current_user.id,
            )
            db.session.add(post)
            db.session.flush()
            log_action("Created blog post", "BlogPosts", post.id)
            flash("Blog post created.", "success")

        db.session.commit()
        return redirect(url_for("admin.blogs"))

    rows = BlogPosts.query.order_by(BlogPosts.created_at.desc()).all()
    return render_template("admin/blogs.html", posts=rows, blog_to_edit=blog_to_edit)


@admin_bp.route("/blogs/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_blog(post_id):
    gate = admin_only_required()
    if gate:
        return gate

    post = BlogPosts.query.get_or_404(post_id)
    db.session.delete(post)
    log_action("Deleted blog post", "BlogPosts", post_id)
    db.session.commit()
    flash("Blog post deleted.", "success")
    return redirect(url_for("admin.blogs"))


@admin_bp.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    gate = admin_only_required()
    if gate:
        return gate

    edit_id = request.args.get("edit", type=int)
    project_to_edit = PortfolioProjects.query.get(edit_id) if edit_id else None

    if request.method == "POST":
        form_id = request.form.get("id", type=int)
        title = request.form.get("title", "").strip()
        summary = request.form.get("summary", "").strip()
        description = request.form.get("description", "").strip()
        tech_stack = request.form.get("tech_stack", "").strip()
        project_url = request.form.get("project_url", "").strip()
        github_url = request.form.get("github_url", "").strip()
        cover_image = request.form.get("cover_image", "").strip()
        featured = request.form.get("featured") == "on"

        if not all([title, summary, description, tech_stack]):
            flash("Please complete required project fields.", "danger")
            return redirect(url_for("admin.projects"))

        if form_id:
            project = PortfolioProjects.query.get_or_404(form_id)
            project.title = title
            project.summary = summary
            project.description = description
            project.tech_stack = tech_stack
            project.project_url = project_url
            project.github_url = github_url
            project.cover_image = cover_image
            project.featured = featured
            if not project.slug:
                project.slug = build_unique_slug(PortfolioProjects, title, "project")
            log_action("Updated project", "PortfolioProjects", project.id)
            flash("Project updated.", "success")
        else:
            project = PortfolioProjects(
                title=title,
                slug=build_unique_slug(PortfolioProjects, title, "project"),
                summary=summary,
                description=description,
                tech_stack=tech_stack,
                project_url=project_url,
                github_url=github_url,
                cover_image=cover_image,
                featured=featured,
            )
            db.session.add(project)
            db.session.flush()
            log_action("Created project", "PortfolioProjects", project.id)
            flash("Project added.", "success")

        db.session.commit()
        return redirect(url_for("admin.projects"))

    rows = PortfolioProjects.query.order_by(PortfolioProjects.created_at.desc()).all()
    return render_template("admin/projects.html", projects=rows, project_to_edit=project_to_edit)


@admin_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def delete_project(project_id):
    gate = admin_only_required()
    if gate:
        return gate

    project = PortfolioProjects.query.get_or_404(project_id)
    db.session.delete(project)
    log_action("Deleted project", "PortfolioProjects", project_id)
    db.session.commit()
    flash("Project deleted.", "success")
    return redirect(url_for("admin.projects"))


@admin_bp.route("/testimonials", methods=["GET", "POST"])
@login_required
def testimonials():
    gate = admin_only_required()
    if gate:
        return gate

    edit_id = request.args.get("edit", type=int)
    row_to_edit = Testimonials.query.get(edit_id) if edit_id else None

    if request.method == "POST":
        form_id = request.form.get("id", type=int)
        client_name = request.form.get("client_name", "").strip()
        company = request.form.get("company", "").strip()
        testimonial = request.form.get("testimonial", "").strip()
        rating = request.form.get("rating", type=int, default=5)
        is_featured = request.form.get("is_featured") == "on"

        if not all([client_name, testimonial]):
            flash("Client name and testimonial are required.", "danger")
            return redirect(url_for("admin.testimonials"))

        if form_id:
            row = Testimonials.query.get_or_404(form_id)
            row.client_name = client_name
            row.company = company
            row.testimonial = testimonial
            row.rating = rating
            row.is_featured = is_featured
            log_action("Updated testimonial", "Testimonials", row.id)
            flash("Testimonial updated.", "success")
        else:
            row = Testimonials(
                client_name=client_name,
                company=company,
                testimonial=testimonial,
                rating=rating,
                is_featured=is_featured,
            )
            db.session.add(row)
            db.session.flush()
            log_action("Created testimonial", "Testimonials", row.id)
            flash("Testimonial added.", "success")

        db.session.commit()
        return redirect(url_for("admin.testimonials"))

    rows = Testimonials.query.order_by(Testimonials.created_at.desc()).all()
    return render_template("admin/testimonials.html", testimonials=rows, testimonial_to_edit=row_to_edit)


@admin_bp.route("/testimonials/<int:testimonial_id>/delete", methods=["POST"])
@login_required
def delete_testimonial(testimonial_id):
    gate = admin_only_required()
    if gate:
        return gate

    row = Testimonials.query.get_or_404(testimonial_id)
    db.session.delete(row)
    log_action("Deleted testimonial", "Testimonials", testimonial_id)
    db.session.commit()
    flash("Testimonial deleted.", "success")
    return redirect(url_for("admin.testimonials"))


@admin_bp.route("/plans", methods=["GET", "POST"])
@login_required
def plans():
    gate = admin_only_required()
    if gate:
        return gate

    edit_id = request.args.get("edit", type=int)
    plan_to_edit = PlanCatalog.query.get(edit_id) if edit_id else None

    if request.method == "POST":
        form_id = request.form.get("id", type=int)
        category = request.form.get("category", "").strip()
        name = request.form.get("name", "").strip()
        price_one_time = request.form.get("price_one_time", "").strip() or None
        price_monthly = request.form.get("price_monthly", "").strip() or None
        best_for = request.form.get("best_for", "").strip()
        features = request.form.get("features", "").strip()
        is_recommended = request.form.get("is_recommended") == "on"

        if not all([category, name, best_for, features]):
            flash("Category, plan name, best-for and features are required.", "danger")
            return redirect(url_for("admin.plans"))

        if form_id:
            row = PlanCatalog.query.get_or_404(form_id)
            row.category = category
            row.name = name
            row.price_one_time = price_one_time
            row.price_monthly = price_monthly
            row.best_for = best_for
            row.features = features
            row.is_recommended = is_recommended
            log_action("Updated plan", "PlanCatalog", row.id)
            flash("Plan updated.", "success")
        else:
            row = PlanCatalog(
                category=category,
                name=name,
                price_one_time=price_one_time,
                price_monthly=price_monthly,
                best_for=best_for,
                features=features,
                is_recommended=is_recommended,
            )
            db.session.add(row)
            db.session.flush()
            log_action("Created plan", "PlanCatalog", row.id)
            flash("Plan created.", "success")

        db.session.commit()
        return redirect(url_for("admin.plans"))

    rows = PlanCatalog.query.order_by(PlanCatalog.category, PlanCatalog.id).all()
    return render_template("admin/plans.html", plans=rows, plan_to_edit=plan_to_edit)


@admin_bp.route("/plans/<int:plan_id>/delete", methods=["POST"])
@login_required
def delete_plan(plan_id):
    gate = admin_only_required()
    if gate:
        return gate

    row = PlanCatalog.query.get_or_404(plan_id)
    db.session.delete(row)
    log_action("Deleted plan", "PlanCatalog", plan_id)
    db.session.commit()
    flash("Plan deleted.", "success")
    return redirect(url_for("admin.plans"))


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    gate = admin_only_required()
    if gate:
        return gate

    settings_row = get_or_create_site_settings()

    if request.method == "POST":
        form_action = request.form.get("form_action", "social")
        if form_action == "social":
            settings_row.instagram_url = normalize_url(request.form.get("instagram_url", ""))
            settings_row.x_url = normalize_url(request.form.get("x_url", ""))
            settings_row.linkedin_url = normalize_url(request.form.get("linkedin_url", ""))
            settings_row.facebook_url = normalize_url(request.form.get("facebook_url", ""))
            settings_row.whatsapp_number = request.form.get("whatsapp_number", "").strip() or "+91 9674667587"

            log_action("Updated site settings", "SiteSettings", settings_row.id)
            db.session.commit()
            flash("Footer links and WhatsApp settings updated.", "success")
            return redirect(url_for("admin.settings"))

        if form_action == "credentials":
            current_password = request.form.get("current_password", "")
            if not current_password or not current_user.check_password(current_password):
                flash("Current password verification failed.", "danger")
                return redirect(url_for("admin.settings"))

            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone_number = request.form.get("phone_number", "").strip()
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not full_name or not email:
                flash("Name and email are required.", "danger")
                return redirect(url_for("admin.settings"))

            existing_admin = AdminUser.query.filter(AdminUser.email == email, AdminUser.id != current_user.id).first()
            if existing_admin:
                flash("Email already in use by another admin.", "danger")
                return redirect(url_for("admin.settings"))

            if new_password:
                if len(new_password) < 8:
                    flash("New password must be at least 8 characters.", "danger")
                    return redirect(url_for("admin.settings"))
                if new_password != confirm_password:
                    flash("New password and confirm password do not match.", "danger")
                    return redirect(url_for("admin.settings"))
                current_user.set_password(new_password)

            current_user.full_name = full_name
            current_user.email = email
            current_user.phone_number = phone_number
            log_action("Updated admin credentials", "AdminUser", current_user.id)
            db.session.commit()
            flash("Credentials updated successfully.", "success")
            return redirect(url_for("admin.settings"))

        flash("Invalid settings action.", "danger")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", settings_row=settings_row)
