from collections import defaultdict

from flask import Blueprint, Response, current_app, render_template, request, url_for

from extensions import db
from models import BlogPosts, PlanCatalog, PortfolioProjects, Testimonials
from routes.shared import DEFAULT_PLAN_DATA, MAINTENANCE_PLAN_DATA, PLAN_DROPDOWN_OPTIONS

main_bp = Blueprint("main", __name__)
GST_RATE = 0.18


def parse_price_value(raw_price):
    text = (raw_price or "").strip()
    if not text:
        return None

    digits_only = "".join(ch for ch in text if ch.isdigit())
    if not digits_only:
        return None

    numeric_value = int(digits_only)
    if numeric_value <= 0:
        return None

    adjusted_value = max(numeric_value - 1, 0)
    suffix = "/month" if "/month" in text.lower() else ""
    has_plus = "+" in text
    return {
        "value": adjusted_value,
        "suffix": suffix,
        "has_plus": has_plus,
    }


def format_inr(value):
    return f"₹{value:,}"


def get_price_view(raw_price, empty_label):
    parsed = parse_price_value(raw_price)
    if not parsed:
        return {
            "display": empty_label,
            "has_breakdown": False,
            "base_display": "",
            "gst_display": "",
            "total_display": "",
            "note": "GST @18% will be added on final billing.",
        }

    value = parsed["value"]
    gst_amount = round(value * GST_RATE)
    total_amount = value + gst_amount
    plus_suffix = "+" if parsed["has_plus"] else ""
    period_suffix = parsed["suffix"]
    return {
        "display": f"{format_inr(value)}{plus_suffix}{period_suffix}",
        "has_breakdown": True,
        "base_display": f"{format_inr(value)}{plus_suffix}{period_suffix}",
        "gst_display": f"{format_inr(gst_amount)}{plus_suffix}{period_suffix}",
        "total_display": f"{format_inr(total_amount)}{plus_suffix}{period_suffix}",
        "note": "",
    }


def ensure_plans_seeded():
    if PlanCatalog.query.first():
        return
    for plan in DEFAULT_PLAN_DATA:
        db.session.add(PlanCatalog(**plan))
    db.session.commit()


@main_bp.route("/")
def home():
    ensure_plans_seeded()

    plan_rows = PlanCatalog.query.order_by(PlanCatalog.category, PlanCatalog.id).all()
    plans_by_category = defaultdict(list)
    for plan in plan_rows:
        plan.features_list = [line.strip() for line in plan.features.split("\n") if line.strip()]
        maintenance_info = MAINTENANCE_PLAN_DATA.get(plan.category, {}).get(plan.name)
        one_time_view = get_price_view(plan.price_one_time, "Not offered as one-time")
        maintenance_raw_price = plan.price_monthly or (maintenance_info or {}).get("price_monthly")
        maintenance_view = get_price_view(maintenance_raw_price, "Custom Quote")

        plan.one_time_display = one_time_view["display"]
        plan.one_time_base_display = one_time_view["base_display"]
        plan.one_time_gst_display = one_time_view["gst_display"]
        plan.one_time_total_display = one_time_view["total_display"]
        plan.one_time_has_breakdown = one_time_view["has_breakdown"]
        plan.one_time_note = one_time_view["note"]

        plan.maintenance_price = maintenance_view["display"]
        plan.maintenance_base_display = maintenance_view["base_display"]
        plan.maintenance_gst_display = maintenance_view["gst_display"]
        plan.maintenance_total_display = maintenance_view["total_display"]
        plan.maintenance_has_breakdown = maintenance_view["has_breakdown"]
        plan.maintenance_note = maintenance_view["note"]

        plan.maintenance_best_for = (maintenance_info or {}).get("best_for") or plan.best_for
        plan.maintenance_description = (maintenance_info or {}).get(
            "description"
        ) or "Monthly maintenance to keep your system secure, optimized, and running smoothly."
        plan.maintenance_features = (maintenance_info or {}).get("features") or plan.features_list
        plans_by_category[plan.category].append(plan)

    featured_projects = PortfolioProjects.query.order_by(PortfolioProjects.featured.desc(), PortfolioProjects.created_at.desc()).limit(6).all()
    testimonials = Testimonials.query.filter_by(is_featured=True).order_by(Testimonials.created_at.desc()).limit(6).all()
    blogs = BlogPosts.query.filter_by(is_published=True).order_by(BlogPosts.created_at.desc()).limit(3).all()

    return render_template(
        "index.html",
        plans_by_category=dict(plans_by_category),
        featured_projects=featured_projects,
        testimonials=testimonials,
        latest_blogs=blogs,
        plan_dropdown_options=PLAN_DROPDOWN_OPTIONS,
    )


@main_bp.route("/blog")
def blog_list():
    posts = BlogPosts.query.filter_by(is_published=True).order_by(BlogPosts.created_at.desc()).all()
    return render_template("blog_list.html", posts=posts)


@main_bp.route("/blog/<slug>")
def blog_detail(slug):
    post = BlogPosts.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("blog_detail.html", post=post)


@main_bp.route("/portfolio")
def portfolio():
    projects = PortfolioProjects.query.order_by(PortfolioProjects.featured.desc(), PortfolioProjects.created_at.desc()).all()
    return render_template("portfolio.html", projects=projects)


@main_bp.route("/inquiry")
def inquiry_page():
    ensure_plans_seeded()

    service_order = [
        "Website Development",
        "E-Commerce Development",
        "Python Automation",
        "AI Chatbot",
        "SEO Services",
    ]
    selected_service = request.args.get("service_type", "").strip()
    selected_plan = request.args.get("plan_name", "").strip()

    rows = PlanCatalog.query.order_by(PlanCatalog.category, PlanCatalog.id).all()
    plans_by_service = {}
    for row in rows:
        maintenance_info = MAINTENANCE_PLAN_DATA.get(row.category, {}).get(row.name)
        one_time = get_price_view(row.price_one_time, "N/A")["display"]
        monthly = get_price_view(row.price_monthly or (maintenance_info or {}).get("price_monthly"), "N/A")["display"]
        label = f"{row.name} (One-Time: {one_time} | Monthly: {monthly})"
        plans_by_service.setdefault(row.category, []).append(
            {
                "name": row.name,
                "label": label,
            }
        )

    ordered_services = [service for service in service_order if service in plans_by_service]
    for service in plans_by_service:
        if service not in ordered_services:
            ordered_services.append(service)

    if selected_service not in ordered_services:
        selected_service = ""

    return render_template(
        "inquiry.html",
        service_options=ordered_services,
        plans_by_service=plans_by_service,
        selected_service=selected_service,
        selected_plan=selected_plan,
    )


@main_bp.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("legals/terms_and_conditions.html")


@main_bp.route("/privacy-policy")
def privacy_policy():
    return render_template("legals/privacy_policy.html")


@main_bp.route("/refund-policy")
def refund_policy():
    return render_template("legals/refund_policy.html")


@main_bp.route("/cookies-policy")
def cookies_policy():
    return render_template("legals/cookies_policy.html")


@main_bp.route("/500")
def error_500_preview():
    return render_template("500.html"), 500


@main_bp.route("/robots.txt")
def robots_txt():
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {url_for('main.sitemap_xml', _external=True)}",
    ]
    return Response("\n".join(lines), mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap_xml():
    pages = []
    static_endpoints = [
        "main.home",
        "main.blog_list",
        "main.portfolio",
        "main.inquiry_page",
        "main.terms_and_conditions",
        "main.privacy_policy",
        "main.refund_policy",
        "main.cookies_policy",
    ]
    for endpoint in static_endpoints:
        pages.append(url_for(endpoint, _external=True))

    posts = BlogPosts.query.filter_by(is_published=True).all()
    projects = PortfolioProjects.query.all()
    for post in posts:
        pages.append(url_for("main.blog_detail", slug=post.slug, _external=True))
    for project in projects:
        pages.append(url_for("main.portfolio", _external=True) + f"#{project.slug}")

    sitemap_body = render_template("sitemap.xml", pages=pages)
    return Response(sitemap_body, mimetype="application/xml")
