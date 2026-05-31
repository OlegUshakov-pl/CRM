![image](image.png)

# CRM

A modern CRM built with **Django 6.0.5 + Tailwind CSS 4 + Alpine.js + HTMX**.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0.5, Python 3.14+ |
| **Frontend** | Tailwind CSS 4, Alpine.js 3, HTMX 2.0, Lucide Icons |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Font** | Montserrat |

## Features

- **Dashboard** — Stats overview, recent projects, today's tasks, recent notes
- **Projects** — Full CRUD with status tracking, gallery, materials, notes, contacts
- **Companies** — Company management with logo upload
- **Contacts** — Contact management linked to companies
- **Materials** — BOM management per project (quantity, unit, price)
- **Tasks** — Task management with priorities, statuses, assignments
- **Notes** — Universal notes linked to projects, companies, contacts
- **Dark Mode** — Toggle light/dark theme
- **Slide-over Forms** — All create/edit via animated right panel
- **Live Search** — HTMX-powered search and filters
- **Responsive** — Mobile-friendly layout with collapsible sidebar
- **Activity Logging** — Automatic tracking of all create/update/delete actions
- **Soft Delete** — All records preserved with `is_active` flag
- **Auto Versioning** — Version displayed in footer, derived from git commit count

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd CRM

# Install Python dependencies
python -m pip install -r requirements.txt

# Install Node dependencies
npm install

# Build Tailwind CSS
npm run build

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start dev server
python manage.py runserver
```

## Project Structure

```
config/              # Django project settings & root URLs
accounts/            # Auth (login, logout, profile)
core/                # Dashboard, base model (TimeStampedModel), activity logging, version
companies/           # Company management
contacts/            # Contact management
projects/            # Project management with status, gallery, notes
materials/           # Materials / BOM management (per project)
tasks/               # Task management
notes/               # Universal notes linked to any entity
generator/           # Template app — boilerplate for adding new modules
templates/
  base.html          # Base layout with sidebar, topbar, dark mode toggle
  includes/
    sidebar.html     # Left navigation sidebar
    topbar.html      # Top bar with search & profile
    slide_over.html  # Slide-over panel for forms
    pagination.html  # Pagination component
static/
  src/styles.css     # Tailwind input
  dist/styles.css    # Tailwind output
media/               # User-uploaded files (logos, avatars, project images)
```

## Models

| Model | Key Fields |
|-------|-----------|
| **Company** | name, email, phone, website, address, logo |
| **Contact** | company (FK), first_name, last_name, email, phone, position, avatar |
| **Project** | name, number, description, status, company (FK), contacts (M2M), dates, budget, image |
| **Material** | project (FK), name, quantity, unit, unit_price, notes |
| **Task** | title, description, status, priority, due_date, project (FK), assigned_to (FK), contacts (M2M) |
| **Note** | title, content, date, project (FK), company (FK), contact (FK) |
| **Activity** | user, action, description, timestamp, object (GenericFK) |

All models inherit from `TimeStampedModel` which provides `created_at`, `updated_at`, `created_by`, and `is_active`.

## UX Pattern

All record creation and editing happens through a semi-transparent slide-over panel that slides in from the right side of the screen. This keeps the main content area stable and provides a focused form experience.

## Generator App

The `generator/` directory contains a ready-to-copy template app (`Deal` model — sales pipeline) with full CRUD, forms, views, URLs, admin, and templates. To create a new module:

```bash
cp -r generator <new_app_name>
# Rename models, views, templates, and register in settings.py
```

See `generator/GENERATOR_README.md` for detailed instructions.

## P.S.

The first version. CRM will be updated and I have a lot of ideas about it. I'm working on changes.
You can take CRM and change it for yourself if you want.
