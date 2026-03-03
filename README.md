# Md Adeen Hussain Portfolio (Production-Ready Flask Stack)

Premium personal portfolio + lead engine + admin dashboard built for high-ticket freelance web development and automation clients.

## Stack
- Frontend: HTML5, TailwindCSS (CDN), CSS3, Vanilla JS, Three.js, Chart.js
- Backend: Python, Flask, SQLAlchemy, Flask-Migrate, Flask-Login
- Database: PostgreSQL (SQLite fallback for local quick start)
- Security: CSRF protection, rate limiting, secure cookies, CSP + security headers
- Deployment: Gunicorn + Render-ready `Procfile`

## Folder Structure
```text
project/
├── app.py
├── config.py
├── extensions.py
├── models.py
├── routes/
│   ├── __init__.py
│   ├── admin.py
│   ├── api.py
│   ├── main.py
│   └── shared.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── blog_list.html
│   ├── blog_detail.html
│   ├── portfolio.html
│   ├── sitemap.xml
│   ├── 404.html
│   └── admin/
│       ├── base_admin.html
│       ├── login.html
│       ├── dashboard.html
│       ├── leads.html
│       ├── inquiries.html
│       ├── blogs.html
│       ├── projects.html
│       ├── testimonials.html
│       └── plans.html
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   ├── js/admin.js
│   ├── js/three-hero.js
│   ├── uploads/.gitkeep
│   └── img/.gitkeep
├── migrations/README
├── migrations/versions/33f47b0d9d6d_baseline_schema.py
├── requirements.txt
├── .env.example
├── Procfile
└── README.md
```

## Core Features Implemented
- Futuristic premium landing page with glassmorphism cards, gradients, glow effects
- Dark/Light mode with persistent `localStorage` state
- Three.js animated 3D hero orb
- Animated counters, scroll reveal, card tilt, skeleton loaders, CTA pulse
- Full pricing system with exact requested plans and monthly/one-time toggle
- Contact form + plan inquiry form with AJAX (no page refresh)
- Optional attachment upload (validated + securely saved)
- PostgreSQL lead persistence
- Secure Admin Login (hashed password + session-based auth)
- Admin dashboard with:
  - Monthly Leads Graph
  - Revenue Graph
  - Plan Distribution Pie Chart
  - Service Analytics Chart
  - Traffic Overview chart (dummy)
  - Notification alerts + activity logs
- Admin CRUD modules:
  - Leads + CSV export + delete
  - Inquiries
  - Blog posts
  - Portfolio projects
  - Testimonials
  - Plan catalog updates
- SEO and indexing:
  - OpenGraph tags
  - Schema.org structured data
  - Blog slug URLs
  - `/sitemap.xml`
  - `/robots.txt`

## Database Schema (Models)
Required models included:
- `ContactLeads`
- `PlanInquiries`
- `BlogPosts`
- `AdminUser`
- `PortfolioProjects`
- `Testimonials`
- `AutomationLogs`
- `Payments` (structure placeholder)

Additional scalability models included:
- `PlanCatalog`
- `ActivityLog`
- `NotificationAlert`
- `Product`, `Cart`, `CartItem`, `Orders`, `OrderItems` (optional e-commerce module)

## Local Setup
1. Create and activate venv.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Copy env template:
```bash
cp .env.example .env
```
4. Set `SECRET_KEY` and `DATABASE_URL` in `.env`.
5. Initialize database migrations:
```bash
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```
6. Create admin user:
```bash
flask create-admin
```
7. Seed demo data:
```bash
flask seed-demo
```
8. Run app:
```bash
flask run
```

## Production Run (Gunicorn)
```bash
gunicorn app:app --workers 3 --threads 2 --timeout 120
```

## Render Deployment Steps
1. Push this repo to GitHub.
2. On Render, create a new Web Service from the repo.
3. Set Build Command:
```bash
pip install -r requirements.txt
```
4. Set Start Command:
```bash
gunicorn app:app
```
5. Add environment variables in Render:
- `FLASK_ENV=production`
- `SECRET_KEY=<strong random value>`
- `DATABASE_URL=<render postgres internal url>`
- `ADMIN_EMAIL=<your admin email>`
- `ADMIN_PASSWORD=<your secure password>`
- `ADMIN_NAME=<your name>`
- `SEO_KEYWORDS=<your keyword string>`
6. Run one-off migration command (Render Shell):
```bash
flask db upgrade
flask seed-demo
```

## Security and Performance Notes
- CSRF protection is enabled globally.
- Rate limiting on auth and public form submission endpoints.
- Password hashing via Werkzeug.
- Secure cookie settings and strict security headers.
- Lazy-loaded media and optimized section rendering.
- Clean route design for SEO-friendly URLs.

## Sample Demo Data
Use:
```bash
flask seed-demo
```
This seeds:
- 1 admin account
- service plans
- blog posts
- featured projects
- testimonials
- sample lead + inquiry
- activity logs + alerts

## Mockup Screenshot Guide (Structure)
Capture these screens after running app:
1. Home Hero: 3D canvas + counters + CTA
2. Pricing Grid: Monthly/One-time toggle with recommended glow card
3. Contact + Inquiry block: AJAX forms
4. Admin Login page
5. Dashboard charts and KPI cards
6. Leads management table with CSV export
7. Blogs/Projects/Testimonials CRUD pages

## Important
Set a strong `SECRET_KEY`, rotate credentials, and use Postgres in production.
