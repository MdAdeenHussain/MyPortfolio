import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from flask import Flask, render_template

load_dotenv()

from config import config_by_name
from extensions import csrf, db, limiter, login_manager, migrate
from models import (
    ActivityLog,
    AdminUser,
    AutomationLogs,
    BlogPosts,
    ContactLeads,
    NotificationAlert,
    PlanCatalog,
    PlanInquiries,
    PortfolioProjects,
    Testimonials,
)

def maybe_fallback_to_sqlite(app, env_name):
    """Fallback to SQLite in development when PostgreSQL config is placeholder/unreachable."""
    if env_name == "production":
        return

    db_uri = (app.config.get("SQLALCHEMY_DATABASE_URI") or "").strip()
    if not db_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
        return

    if db_uri.startswith("postgresql://"):
        if "username:password@" in db_uri or "localhost:5432/portfolio_db" in db_uri:
            app.logger.warning("Placeholder DATABASE_URL detected. Falling back to sqlite:///portfolio.db")
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
            return

        try:
            engine = create_engine(db_uri, pool_pre_ping=True, connect_args={"connect_timeout": 3})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            engine.dispose()
        except Exception:
            app.logger.warning("PostgreSQL unavailable in development. Falling back to sqlite:///portfolio.db")
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"


def create_app(config_name=None):
    app = Flask(__name__)

    env_name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(env_name, config_by_name["development"]))
    maybe_fallback_to_sqlite(app, env_name)
    if not app.config.get("SECRET_KEY"):
        if env_name == "production":
            raise RuntimeError("SECRET_KEY must be set in production.")
        app.config["SECRET_KEY"] = os.urandom(32).hex()

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message_category = "warning"

    if env_name != "production" and app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        # Local convenience: prevents "no such table" errors before first migration run.
        with app.app_context():
            db.create_all()

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    from routes.admin import admin_bp
    from routes.api import api_bp
    from routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        return {
            "current_year": datetime.utcnow().year,
            "seo_keywords": app.config.get("SEO_KEYWORDS"),
        }

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers[
            "Content-Security-Policy"
        ] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "connect-src 'self';"
        )
        if os.getenv("FLASK_ENV") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html"), 404

    @app.cli.command("seed-demo")
    def seed_demo():
        seed_demo_data()
        print("Demo data seeded.")

    @app.cli.command("create-admin")
    def create_admin():
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
        full_name = os.getenv("ADMIN_NAME", "Admin")

        admin = AdminUser.query.filter_by(email=email).first()
        if admin:
            print(f"Admin already exists: {email}")
            return

        admin = AdminUser(full_name=full_name, email=email, role="admin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin created: {email}")

    return app


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


def seed_demo_data():
    from routes.shared import DEFAULT_PLAN_DATA

    admin = AdminUser.query.filter_by(email="admin@adeen.dev").first()
    if not admin:
        admin = AdminUser(full_name="Md Adeen Hussain", email="admin@adeen.dev", role="admin")
        admin.set_password("Admin@12345")
        db.session.add(admin)
        db.session.flush()

    if not PlanCatalog.query.first():
        for plan in DEFAULT_PLAN_DATA:
            db.session.add(PlanCatalog(**plan))

    if not BlogPosts.query.first():
        db.session.add_all(
            [
                BlogPosts(
                    title="Why Flask + PostgreSQL Is Perfect for Startup MVPs",
                    slug="why-flask-postgresql-is-perfect-for-startup-mvps",
                    excerpt="A practical architecture for speed, cost control, and scale.",
                    content="Flask gives flexibility while PostgreSQL gives data integrity and analytics depth...",
                    author_id=admin.id,
                    tags="flask,startups,postgresql",
                ),
                BlogPosts(
                    title="Automation Workflows That Save 20+ Hours Per Week",
                    slug="automation-workflows-save-20-hours",
                    excerpt="Process automation opportunities most businesses miss.",
                    content="From lead sync to invoice automation, Python scripts can remove repetitive bottlenecks...",
                    author_id=admin.id,
                    tags="automation,python,ops",
                ),
            ]
        )

    if not PortfolioProjects.query.first():
        db.session.add_all(
            [
                PortfolioProjects(
                    title="D2C Commerce Growth Platform",
                    slug="d2c-commerce-growth-platform",
                    summary="Custom storefront + inventory automation for a lifestyle brand.",
                    description="Built a Flask-driven backend for catalog operations, campaign tracking, and checkout analytics.",
                    tech_stack="Flask, PostgreSQL, Redis, Tailwind",
                    project_url="#",
                    featured=True,
                    cover_image="https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
                ),
                PortfolioProjects(
                    title="CRM Lead Intelligence Dashboard",
                    slug="crm-lead-intelligence-dashboard",
                    summary="Analytics-heavy dashboard for an international agency.",
                    description="Automated lead ingestion, funnel analytics, and sales qualification dashboards.",
                    tech_stack="Flask, Chart.js, PostgreSQL",
                    project_url="#",
                    featured=True,
                    cover_image="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
                ),
            ]
        )

    if not Testimonials.query.first():
        db.session.add_all(
            [
                Testimonials(
                    client_name="Aarav Mehta",
                    company="Nexa Retail",
                    testimonial="Adeen transformed our online pipeline and improved conversions by 42% in 90 days.",
                    rating=5,
                    is_featured=True,
                ),
                Testimonials(
                    client_name="Sophia Reynolds",
                    company="ScaleOps UK",
                    testimonial="Clear architecture, great communication, and production-quality delivery.",
                    rating=5,
                    is_featured=True,
                ),
            ]
        )

    if not AutomationLogs.query.first():
        db.session.add_all(
            [
                AutomationLogs(service_name="Lead Sync", status="healthy", details="Webhook + CRM sync stable", execution_time_ms=312),
                AutomationLogs(service_name="Invoice Bot", status="warning", details="Delayed 1 run", execution_time_ms=1299),
                AutomationLogs(service_name="Chatbot Monitor", status="healthy", details="No downtime", execution_time_ms=221),
            ]
        )

    if not NotificationAlert.query.first():
        db.session.add_all(
            [
                NotificationAlert(title="New High-Ticket Inquiry", body="Growth Website Plan requested from Dubai", severity="info"),
                NotificationAlert(title="Automation Alert", body="Invoice Bot had a delayed trigger", severity="warning"),
            ]
        )

    if not ContactLeads.query.first():
        db.session.add(
            ContactLeads(
                full_name="Rohan B.",
                email="rohan@example.com",
                company="Brightline Ventures",
                phone="+91-9000000000",
                selected_plan="Growth Website Plan",
                budget="₹50,000 - ₹1,00,000",
                message="Need a conversion-focused website with CRM integration.",
            )
        )

    if not PlanInquiries.query.first():
        db.session.add(
            PlanInquiries(
                full_name="Emma Carter",
                email="emma@agencypro.io",
                service_type="AI Chatbot",
                plan_name="Smart GPT",
                timeline="3 weeks",
                budget="₹50,000 - ₹1,00,000",
                project_details="Looking for GPT support + FAQ and CRM sync.",
            )
        )

    db.session.add(
        ActivityLog(
            actor_email=admin.email,
            action="Seeded demo portfolio data",
            entity="system",
            entity_id=0,
        )
    )

    db.session.commit()


app = create_app()


if __name__ == "__main__":
    app.run()
