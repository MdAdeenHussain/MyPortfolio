from collections import defaultdict

from flask import Blueprint, Response, current_app, render_template, request, url_for

from extensions import db
from models import BlogPosts, PlanCatalog, PortfolioProjects, Testimonials
from routes.shared import DEFAULT_PLAN_DATA, PLAN_DROPDOWN_OPTIONS

main_bp = Blueprint("main", __name__)


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
