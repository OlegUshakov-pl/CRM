![CRM-gif](CRM.gif)
# CRM

**Django 6.0.6 + Tailwind CSS 4 + Alpine.js + HTMX + Ollama AI**

A project management, contractor and task tracking system for engineering and manufacturing businesses.

---

## Quick Start

```bash
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
npm install
npm run build
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Alternatively, run `install.bat` for one-click setup. Use `update.bat` to pull latest changes.

---

## Tech Stack

| Layer    | Technology |
|----------|-----------|
| Backend  | Django 6.0.6, Python 3.14+, SQLite |
| Frontend | Tailwind CSS 4, Alpine.js 3, HTMX 2.0, Lucide Icons |
| AI       | Ollama (local LLM) with rule-based command processing |

---

## Modules

| Module | Description |
|--------|-------------|
| **Dashboard** | Key metrics, recent projects, tasks, notes |
| **Companies** | Company directory with contacts and details |
| **Contacts** | Contacts linked to companies |
| **Projects** | Full lifecycle: statuses, budget, dates, image gallery, ZIP export/import |
| **Materials/BOM** | Bill of Materials per project with categories and pricing |
| **Tasks** | Prioritized tasks with statuses, due dates, filtering |
| **Library** | Knowledge base with rich text (Quill.js), files, categories, tags, favorites |
| **Notes** | Universal notes linkable to projects, companies, contacts |
| **Documents** | File upload with preview (images, PDF, text) |
| **Parts** | Engineering drawings and 3D models (.stp, .ipt, .sldprt, .ics, .sldasm, .iam) |
| **Calendar** | Three-month calendar view with navigation |
| **Generator** | Module scaffolding template for rapid prototyping |

## Cross-cutting Features

- **Slide-over forms** — CRUD via HTMX without page navigation
- **Soft delete** — `is_active` flag on all entities
- **Global search** — single page search across all entity types
- **Activity logging** — all changes tracked via Generic Foreign Key
- **Project export/import** — full project data as ZIP archives
- **Dark mode** — persisted via localStorage
- **Responsive design** — desktop and mobile
- **Collapsible sidebar** — expandable navigation
- **Settings panel** — configurable storage paths and naming

---

## AI Assistant

Powered by **Ollama** with two modes:

- **CHAT** — free conversation with any installed Ollama model
- **COMMANDS** — natural-language CRM actions (rule-based intent detection)

### Setup

1. Install [Ollama](https://ollama.com)
2. Pull a model: `ollama pull llama3.2`
3. Start Ollama (runs on port 11434 by default)
4. Select the model in the CRM chat interface

### Example Commands

```
Create project 001, Office Building on 2026-06-15
Add task Call client on 2026-06-10
Find contact Ivan
Add material Bolt 50 to project Test
Upload file drawing.pdf to project Test
Show all drawings of project Test
Create note Meeting for project Test
Open bbc.com
Download file from https://example.com/image.png
Create file hello.py with content print("Hello, World!")
Search for latest Python 3.14 features
Find pdf on site https://example.com
```

### Capabilities

Browser agent, web search (DuckDuckGo), AI file management, 10-second undo, audit logging, model selection, confirmation flow for write operations.

---

## Project Structure

```
CRM/
  config/            Settings, root URL config, WSGI/ASGI
  accounts/          Authentication
  core/              Dashboard, base models, activity log, search
  companies/         Company management
  contacts/          Contact management
  projects/          Project management, export/import
  materials/         Bill of Materials
  tasks/             Task management
  notes/             Universal notes
  documents/         File upload with preview
  library/           Knowledge base (rich text, files, tags)
  parts/             Drawings and 3D models
  assistant/         AI chat, services (LLM, browser, files)
  calendar_app/      Calendar view
  generator/         Module scaffolding template
  templates/         Base layout, includes (sidebar, topbar, chat)
  static/            Tailwind CSS source
  media/             User-uploaded files
  ai_files/          AI-downloaded files
```

## URL Routing

| Prefix | App |
|--------|-----|
| `/admin/` | Django Admin |
| `/` | core (dashboard, search, help, settings) |
| `/accounts/` | accounts |
| `/companies/` | companies |
| `/contacts/` | contacts |
| `/projects/` | projects |
| `/tasks/` | tasks |
| `/notes/` | notes |
| `/materials/` | materials |
| `/deals/` | generator |
| `/documents/` | documents |
| `/library/` | library |
| `/parts/` | parts |
| `/assistant/` | assistant |
| `/calendar/` | calendar_app |

---

## Data Models

All business models extend `TimeStampedModel` (abstract base):

| Field | Description |
|-------|-------------|
| `created_at` | Auto-set on creation |
| `updated_at` | Auto-updated on save |
| `created_by` | ForeignKey to User (nullable) |
| `is_active` | Boolean for soft-delete |

| Model | Key Fields | Relationships |
|-------|------------|---------------|
| **Company** | name, slug, email, phone, website, address, logo, notes | Referenced by Contact, Project, Note, Deal |
| **Contact** | first_name, last_name, slug, email, phone, position, avatar, notes | FK→Company; M2M→Project, Deal |
| **Project** | name, slug, number, description, status, dates, budget, image | FK→Company; M2M→Contact |
| **ProjectImage** | image, uploaded_at | FK→Project |
| **Material** | name, slug, quantity, unit, unit_price, notes | FK→Project, Category |
| **Task** | title, slug, description, status, priority, due_date | FK→Project |
| **Note** | title, slug, content, date | FK→Project/Company/Contact |
| **Document** | number, size, file, file_type | FK→Project |
| **LibraryItem** | title, slug, content, description, file, file_type, is_favorite | FK→Category; M2M→Tag |
| **Part** | number, size, rev, file | FK→Project, Category |
| **Deal** | name, slug, description, status, priority, value, due_date | FK→Company; M2M→Contact; FK→User |
| **ChatSession** | user, title, is_active, last_message_at | Per-user AI sessions |
| **ChatMessage** | session, role, kind, content, payload | Chat messages |
| **AIFile** | owner, file, original_name, source_url, size, category | AI-downloaded files |
| **AILog** | user, session, action, status, description, request/response, duration_ms | AI audit log |
| **Activity** | user, action, description, content_type, object_id | Global activity log |
| **AppSetting** | key, value | Key-value settings |

---

## File System Architecture

```
{project_number}_{project_name}_Project/
  documents/
  drawings/
  models/
```

Subfolder naming is configurable via `AppSetting`.

---

## Development

```bash
# Watch Tailwind
npm run dev

# Production build
npm run build

# Collect static files
python manage.py collectstatic

# Run server
python manage.py runserver
```

## Architecture Highlights

- Slide-over forms via HTMX with AJAX-loaded sliding panels
- Project files stored in organized disk subdirectories
- AI intent detection via regex patterns (no NLP model required)
- Write operations require two-step confirmation
- Versioning: `1.2.{git_commit_count}`
- Clean RESTful URLs with slugs
