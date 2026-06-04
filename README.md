![image](image.png)

# CRM

A modern CRM built with **Django 6.0.6 + Tailwind CSS 4 + Alpine.js + HTMX**.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0.6, Python 3.14+ |
| **Frontend** | Tailwind CSS 4, Alpine.js 3, HTMX 2.0, Lucide Icons |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Font** | Montserrat |

## Features

- **Dashboard** — stats, recent projects, today's tasks, recent notes
- **Projects** — full CRUD with status, gallery, materials, notes, contacts
- **Companies** — management with logo upload
- **Contacts** — linked to companies
- **Materials** — BOM per project (quantity, unit, price)
- **Tasks** — priorities, statuses, due dates
- **Notes** — linked to projects, companies, contacts
- **Documents** — upload, preview (images, PDF, text), download, filter by type/project/category, multiple file upload
- **Dark mode** — light/dark toggle
- **Slide-over forms** — create/edit via animated right panel
- **Live search** — HTMX-powered search and filters
- **Sorting** — column-based sort on tables (materials, documents, notes, categories)
- **Responsive** — mobile-friendly with collapsible sidebar
- **Activity logging** — automatic tracking of all CUD actions
- **Soft delete** — all records preserved via `is_active`
- **Auto versioning** — version from git commit count

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
config/              Settings & root URLs
accounts/            Auth (login, logout, profile)
core/                Dashboard, base model, activity logging
companies/           Company management
contacts/            Contact management
projects/            Project management
materials/           Materials / BOM
tasks/               Task management
notes/               Universal notes
documents/           File management with preview (images, PDF, text)
generator/           Template app for new modules
templates/
  base.html          Base layout
  includes/          Sidebar, topbar, slide-over, pagination
static/
  src/styles.css     Tailwind input
  dist/styles.css    Tailwind output
media/               Uploaded files (logos, avatars, images)
documents/           Uploaded documents (grouped by project/type)
```

## Models

| Model | Key Fields |
|-------|-----------|
| **Company** | name, email, phone, website, address, logo |
| **Contact** | company (FK), first_name, last_name, email, phone, position, avatar |
| **Project** | name, number, description, status, company (FK), contacts (M2M), dates, budget, image |
| **Material** | project (FK), name, quantity, unit, unit_price, notes |
| **Task** | title, description, status, priority, due_date, project (FK) |
| **Note** | title, content, date, project (FK), company (FK), contact (FK) |
| **Document** | project (FK, nullable), number, file, file_type (models_3d/documents/drawings/photos/other), size |
| **Activity** | user, action, description, timestamp, object (GenericFK) |

All models inherit from `TimeStampedModel` (`created_at`, `updated_at`, `created_by`, `is_active`).

## UX

All forms use a slide-over panel from the right, keeping the main content stable.

## Generator App

The `generator/` app is a ready-to-copy template with full CRUD. To create a new module:

```bash
cp -r generator <new_app_name>
# Rename models, views, templates, register in settings.py
```

See `generator/GENERATOR_README.md` for details.
