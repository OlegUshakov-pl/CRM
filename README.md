# CRM

<!-- Django 6.0.6 + Tailwind CSS 4 + Alpine.js + HTMX + Ollama AI -->

## Quick Start

```bash
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

## Stack

<!-- Backend: Django 6.0.6, Python 3.14+ -->
<!-- Frontend: Tailwind CSS 4, Alpine.js 3, HTMX 2.0, Lucide Icons -->
<!-- Database: SQLite -->
<!-- Font: Montserrat -->
<!-- AI: Ollama (local LLM) -->

## Apps

<!-- core — Dashboard, TimeStampedModel, Activity logging, AppSetting -->
<!-- accounts — Auth (login, logout, profile) -->
<!-- companies — Company CRUD (name, email, phone, website, address, logo) -->
<!-- contacts — Contact CRUD (linked to companies, avatar) -->
<!-- projects — Project CRUD (status, gallery, materials, notes, contacts, export/import ZIP) -->
<!-- materials — BOM per project (quantity, unit, price, categories) -->
<!-- tasks — Task CRUD (priorities, statuses, due dates) -->
<!-- notes — Notes linked to projects, companies, contacts -->
<!-- documents — File upload with preview (images, PDF, text), filter by type/project/category -->
<!-- parts — Drawings and 3D models (.stp, .ipt, .sldprt, etc.) -->
<!-- assistant — AI chat with Ollama, voice input, browser screenshots, AI Files storage -->
<!-- generator — Template app for new modules -->

## AI Assistant

<!-- Modes: -->
<!--   CHAT — talk to Ollama models (select from installed models) -->
<!--   COMMANDS — CRM commands (create projects, tasks, contacts, etc.) -->
<!-- Voice input via Web Speech API -->
<!-- Browser: open URLs, take screenshots, extract titles and PDF links -->
<!-- AI Files: download files from web, attach to projects, manage storage -->
<!-- Undo: 10-second undo window for create/delete actions -->
<!-- All actions logged to AILog -->

## Commands

```bash
# Create project
"Create project 001, Office Building on 2026-06-15"

# Add task
"Add task Call client on 2026-06-10"

# Find contact
"Find contact Ivan"

# Add material
"Add material Bolt 50 to project Test"

# Upload document
"Upload file drawing.pdf to project Test"

# Show drawings
"Show all drawings of project Test"

# Show company
"What is the company of project Test"

# Create note
"Create note Meeting for project Test"

# Open website
"Open bbc.com"

# Download file
"Download file from https://example.com/image.png"
```

## Models

<!-- Company — name, email, phone, website, address, logo -->
<!-- Contact — company (FK), first_name, last_name, email, phone, position, avatar -->
<!-- Project — name, number, description, status, company (FK), contacts (M2M), dates, budget, image -->
<!-- Material — project (FK), category (FK), name, quantity, unit, unit_price, notes -->
<!-- Task — title, description, status, priority, due_date, project (FK) -->
<!-- Note — title, content, date, project (FK), company (FK), contact (FK) -->
<!-- Document — project (FK), number, file, file_type, size -->
<!-- Part — project (FK), category (FK), number, size, rev, file -->
<!-- ChatSession — user, title, is_active, last_message_at -->
<!-- ChatMessage — session (FK), role, kind, content, payload -->
<!-- AIFile — owner (FK), file, original_name, source_url, size, category -->
<!-- AILog — user, session (FK), action, status, description, request/response text, payload -->
<!-- Activity — user, action, description, content_type, object_id (GenericFK) -->

<!-- All models inherit TimeStampedModel (created_at, updated_at, created_by, is_active) -->

## Structure

```
config/          Settings, root URLs
accounts/        Auth
core/            Dashboard, base models, activity logging
companies/       Company management
contacts/        Contact management
projects/        Project management, export/import
materials/       Materials / BOM
tasks/           Task management
notes/           Universal notes
documents/       File management with preview
parts/           Drawings and 3D models
assistant/       AI chat, Ollama, browser, AI Files
generator/       Template for new modules
templates/       Base layout, includes
static/          Tailwind CSS (src -> dist)
media/           Uploaded files
```

<!-- Ollama: http://localhost:11434 (configurable in settings.py OLLAMA_BASE_URL) -->
