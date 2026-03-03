import re
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import event
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def slugify(value):
    value = re.sub(r"[^a-zA-Z0-9\s-]", "", value).strip().lower()
    value = re.sub(r"[\s_-]+", "-", value)
    return value


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ContactLeads(db.Model, TimestampMixin):
    __tablename__ = "contact_leads"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False, index=True)
    company = db.Column(db.String(180))
    phone = db.Column(db.String(40))
    selected_plan = db.Column(db.String(120))
    budget = db.Column(db.String(50))
    message = db.Column(db.Text, nullable=False)
    attachment_path = db.Column(db.String(255))
    source = db.Column(db.String(120), default="portfolio-contact")
    status = db.Column(db.String(50), default="new", index=True)


class PlanInquiries(db.Model, TimestampMixin):
    __tablename__ = "plan_inquiries"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), nullable=False, index=True)
    service_type = db.Column(db.String(120), nullable=False, index=True)
    plan_name = db.Column(db.String(120), nullable=False)
    project_details = db.Column(db.Text, nullable=False)
    timeline = db.Column(db.String(80))
    budget = db.Column(db.String(50))
    status = db.Column(db.String(50), default="pending", index=True)


class BlogPosts(db.Model, TimestampMixin):
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(220), nullable=False, unique=True, index=True)
    excerpt = db.Column(db.String(280), nullable=False)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=True)
    tags = db.Column(db.String(255), default="flask,web,automation")
    author_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"), nullable=False)


class AdminUser(UserMixin, db.Model, TimestampMixin):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="admin")
    is_active_admin = db.Column(db.Boolean, default=True)

    posts = db.relationship("BlogPosts", backref="author", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.is_active_admin


class PortfolioProjects(db.Model, TimestampMixin):
    __tablename__ = "portfolio_projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(220), nullable=False, unique=True, index=True)
    summary = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.String(255), nullable=False)
    project_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    cover_image = db.Column(db.String(255))
    featured = db.Column(db.Boolean, default=False)


class Testimonials(db.Model, TimestampMixin):
    __tablename__ = "testimonials"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(180))
    testimonial = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    client_image = db.Column(db.String(255))
    is_featured = db.Column(db.Boolean, default=True)


class AutomationLogs(db.Model):
    __tablename__ = "automation_logs"

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(120), nullable=False, index=True)
    status = db.Column(db.String(40), nullable=False, index=True)
    details = db.Column(db.Text)
    execution_time_ms = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)


class Payments(db.Model, TimestampMixin):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    client_email = db.Column(db.String(180), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(8), default="INR")
    payment_gateway = db.Column(db.String(50), default="placeholder")
    transaction_id = db.Column(db.String(150), unique=True)
    status = db.Column(db.String(40), default="initiated")
    notes = db.Column(db.Text)


class PlanCatalog(db.Model, TimestampMixin):
    __tablename__ = "plan_catalog"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(120), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    price_one_time = db.Column(db.String(60))
    price_monthly = db.Column(db.String(60))
    best_for = db.Column(db.String(180), nullable=False)
    features = db.Column(db.Text, nullable=False)
    is_recommended = db.Column(db.Boolean, default=False)


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    actor_email = db.Column(db.String(180), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    entity = db.Column(db.String(120), nullable=False)
    entity_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)


class NotificationAlert(db.Model):
    __tablename__ = "notification_alerts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    body = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(20), default="info")
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class SiteSettings(db.Model, TimestampMixin):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    instagram_url = db.Column(db.String(255), default="")
    x_url = db.Column(db.String(255), default="")
    linkedin_url = db.Column(db.String(255), default="")
    facebook_url = db.Column(db.String(255), default="")
    whatsapp_number = db.Column(db.String(30), default="+91 9674667587")


# Optional E-Commerce module
class Product(db.Model, TimestampMixin):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(150), nullable=False, unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)


class Cart(db.Model, TimestampMixin):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(120), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(10, 2), default=0)


class CartItem(db.Model, TimestampMixin):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)


class Orders(db.Model, TimestampMixin):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(100), unique=True, nullable=False)
    client_name = db.Column(db.String(120), nullable=False)
    client_email = db.Column(db.String(180), nullable=False)
    status = db.Column(db.String(40), default="pending")
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_status = db.Column(db.String(40), default="unpaid")


class OrderItems(db.Model, TimestampMixin):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)


@event.listens_for(BlogPosts, "before_insert")
def set_blog_slug_before_insert(_, __, target):
    if target.title and not target.slug:
        target.slug = slugify(target.title)


@event.listens_for(BlogPosts, "before_update")
def set_blog_slug_before_update(_, __, target):
    if target.title and not target.slug:
        target.slug = slugify(target.title)


@event.listens_for(PortfolioProjects, "before_insert")
def set_project_slug_before_insert(_, __, target):
    if target.title and not target.slug:
        target.slug = slugify(target.title)


@event.listens_for(Product, "before_insert")
def set_product_slug_before_insert(_, __, target):
    if target.name and not target.slug:
        target.slug = slugify(target.name)
