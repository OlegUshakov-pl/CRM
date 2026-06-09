![CRM](image.png)
# CRM

**Django 6.0.6 + Tailwind CSS 4 + Alpine.js + HTMX + Ollama AI** — a project management, contractor and task tracking system built for engineering and manufacturing businesses.

---

## Tech Stack

| Layer         | Technology                                       |
|---------------|--------------------------------------------------|
| Backend       | Django 6.0.6, Python 3.14+, SQLite               |
| Frontend      | Tailwind CSS 4, Alpine.js 3, HTMX 2.0, Lucide Icons |
| AI            | Ollama (local LLM), rule-based command processing |
| Font          | Montserrat (Google Fonts)                        |

---

## Features

### Core Modules

| Module       | Description |
|--------------|-------------|
| **Dashboard**    | Home page with key metrics, recent projects, tasks and notes |
| **Companies**    | Company directory (name, email, phone, website, address, logo) |
| **Contacts**     | Contact management linked to companies, with avatars |
| **Projects**     | Full project lifecycle (statuses, budget, dates, image gallery, ZIP export/import) |
| **Materials/BOM**| Bill of Materials per project (quantity, units, prices, categories) |
| **Tasks**        | Task management with priorities, statuses, due dates, and filtering |
| **Notes**        | Universal notes linkable to projects, companies, or contacts |
| **Documents**    | File upload with preview (images, PDF, text), filterable by type and project |
| **Parts**        | Engineering drawings and 3D models (.stp, .ipt, .sldprt, .ics, .sldasm, .iam) |
| **Calendar**     | Three-month calendar view with month/year dropdowns and navigation |
| **Generator**    | Module scaffolding template for rapid prototyping (example: Deal pipeline) |

### Cross-cutting Features

- **Slide-over forms** — CRUD operations via HTMX without page navigation
- **Soft delete** — all entities use `is_active` flag for safe deletion
- **Global search** — search across all entity types from a single page
- **Activity logging** — all changes tracked via Generic Foreign Key (ContentType framework)
- **Project export/import** — full project data packaged as ZIP archives
- **Dark mode** — toggled via localStorage, persisted across sessions
- **Responsive design** — works on desktop and mobile
- **Collapsible sidebar** — expandable navigation panel
- **Settings panel** — configurable project storage paths and subfolder naming

---

## AI Assistant

The built-in AI assistant is powered by **Ollama** (local LLM) with two modes:

- **CHAT** — free conversation with the selected Ollama model; also supports file creation via natural language
- **COMMANDS** — execute CRM actions via natural language (rule-based intent detection, no NLP model required)

### Setup

1. Download and install Ollama from [ollama.com](https://ollama.com)
2. Pull a model (e.g., Llama 3.2, Mistral, or any supported model):
   ```bash
   ollama pull llama3.2
   ```
3. Start Ollama (it runs as a background service by default on port 11434)
4. Select the model in the CRM chat interface — the dropdown lists all installed models automatically

### Example Commands

```
Create project 001, Office Building on 2026-06-15
Add task Call client on 2026-06-10
Find contact Ivan
Add material Bolt 50 to project Test
Upload file drawing.pdf to project Test
Show all drawings of project Test
What is the company of project Test
Create note Meeting for project Test
Open bbc.com
Download file from https://example.com/image.png
Create file hello.py with content print("Hello, World!")
Create file styles.css for a dark theme stylesheet (AI generates content)
Search for latest Python 3.14 features
Find information about Django 6.0 on the internet
What is the capital of France?
Who is Nikola Tesla?
Find pdf on site https://example.com
Find picture with name logo on site https://example.com
Find pdf report on site https://example.com/documents
```

### Capabilities

- **Browser agent** — open URLs, take screenshots, extract titles and PDF links
- **Web search** — search the internet via DuckDuckGo directly from chat
- **Find files on site** — locate PDFs or images on any website by URL and optional name filter
- **AI Files** — download files from the web, create files with AI-generated content, attach to projects, manage storage
- **Undo** — 10-second window to revert create/delete actions
- **Audit logging** — all AI actions logged to `AILog`
- **Model selection** — switch between installed Ollama models at any time
- **Confirmation flow** — write operations require a two-step confirmation

---

## Quick Start

```bash
# Clone the repository
git clone <repo-url> && cd CRM

# Python dependencies
python -m pip install -r requirements.txt

# Node dependencies (Tailwind CLI)
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

The server will be available at **http://127.0.0.1:8000**.

For the AI assistant, a running Ollama instance is required at **http://localhost:11434** (configurable in `settings.py`).

Alternatively, just run `install.bat` to set up the entire system automatically.

To update CRM to the latest version, simply run `update.bat` — it will pull changes, install dependencies, run migrations, and rebuild the frontend.

---

## Project Structure

```
CRM/
  config/            Settings, root URL config, WSGI/ASGI entry points
  accounts/          Authentication (login, logout, profile, password reset)
  core/              Dashboard, TimeStampedModel, Activity log, AppSetting, search, help page
  companies/         Company management
  contacts/          Contact management (linked to companies)
  projects/          Project management, ZIP export/import, image gallery
  materials/         Bill of Materials (BOM) with categories
  tasks/             Task management (priorities, statuses, due dates)
  notes/             Universal notes (linked to projects, companies, contacts)
  documents/         File upload with preview (images, PDF, text)
  parts/             Drawings and 3D models (.stp, .ipt, .sldprt, .ics, etc.)
  assistant/         AI chat (Ollama), browser agent, AI file management, logging
    services/        Command registry, handlers, browser, files, i18n
  calendar_app/      Three-month calendar view with navigation
  generator/         Module scaffolding template (example: Deal pipeline)
  templates/         Base layout and includes
    base.html
    includes/        sidebar, topbar, chat_widget, pagination, slide_over
  static/            Tailwind CSS source (src -> dist)
    src/styles.css
  media/             User-uploaded files
  ai_files/          AI-downloaded files
```

---

## Data Models

All business models inherit from `TimeStampedModel` (abstract base), which provides:

| Field        | Description |
|--------------|-------------|
| `created_at` | Auto-set on creation |
| `updated_at` | Auto-updated on save |
| `created_by` | ForeignKey to User (nullable) |
| `is_active`  | Boolean for soft-delete (default: True) |

### Entity Models

| Model         | Key Fields | Relationships |
|---------------|------------|---------------|
| **Company**   | `name`, `slug`, `email`, `phone`, `website`, `address`, `logo`, `notes` | Referenced by Contact, Project, Note, Deal |
| **Contact**   | `first_name`, `last_name`, `slug`, `email`, `phone`, `position`, `avatar`, `notes` | FK → Company; M2M → Project, Deal |
| **Project**   | `name`, `slug`, `number`, `description`, `status`, `dates`, `budget`, `image` | FK → Company; M2M → Contact |
| **ProjectImage** | `image`, `uploaded_at` | FK → Project (CASCADE) |
| **Material**  | `name`, `slug`, `quantity`, `unit`, `unit_price`, `notes` | FK → Project, Category (materials) |
| **Category** (materials) | `name` | Referenced by Material |
| **Task**      | `title`, `slug`, `description`, `status`, `priority`, `due_date` | FK → Project |
| **Note**      | `title`, `slug`, `content`, `date` | FK → Project, Company, Contact (all nullable) |
| **Document**  | `number`, `size`, `file`, `file_type` | FK → Project |
| **Part**      | `number`, `size`, `rev`, `file` | FK → Project, Category (parts) |
| **Category** (parts) | `name` | Referenced by Part |
| **Deal**      | `name`, `slug`, `description`, `status`, `priority`, `value`, `due_date` | FK → Company; M2M → Contact; FK → User (assigned_to) |

### AI & System Models

| Model          | Key Fields | Purpose |
|----------------|------------|---------|
| **ChatSession**| `user`, `title`, `is_active`, `last_message_at` | Per-user AI chat sessions |
| **ChatMessage**| `session`, `role`, `kind`, `content`, `payload` | Individual chat messages |
| **AIFile**     | `owner`, `file`, `original_name`, `source_url`, `size`, `category` | Files downloaded by AI |
| **AILog**      | `user`, `session`, `action`, `status`, `description`, `request_text`, `response_text`, `payload`, `duration_ms` | Full audit log of AI actions |
| **Activity**   | `user`, `action`, `description`, `content_type`, `object_id` | Global activity log (GenericForeignKey) |
| **AppSetting** | `key` (unique), `value` | Key-value settings store |

---

## File System Architecture

Project files are organized on disk as:

```
{project_number}_{project_name}_Project/
  documents/
  drawings/
  models/
```

Subfolder naming is configurable via `AppSetting` (`subfolder_documents`, `subfolder_drawings`, `subfolder_models`), using `{Number}` as a placeholder for the project number.

---

## Development

### Tailwind CSS

```bash
# Watch mode (auto-rebuild on changes)
npm run dev

# Production build
npm run build
```

### Django

```bash
# Collect static files for production
python manage.py collectstatic

# Run development server
python manage.py runserver
```

---

## Architecture Highlights

- **Slide-over forms** — most CRUD operations use HTMX slide-over panels without page navigation; forms are loaded via AJAX into a sliding panel
- **Project file system** — files stored in organized subdirectories per project
- **AI rules** — intent detection via regex patterns (no NLP model required); all write operations require two-step confirmation before execution
- **AI file creation** — generate and save files in any supported format (code, text, markup, etc.) via natural language in both CHAT and COMMANDS modes; supports inline content or AI-generated content via Ollama
- **Versioning** — app version follows `1.2.{git_commit_count}` format, derived from the number of git commits
- **URL structure** — clean RESTful URLs with slugs for all entities

### URL Routing

| Prefix         | App          |
|----------------|--------------|
| `/admin/`      | Django Admin |
| `/`            | core (dashboard, search, help, settings) |
| `/accounts/`   | accounts |
| `/companies/`  | companies |
| `/contacts/`   | contacts |
| `/projects/`   | projects |
| `/tasks/`      | tasks |
| `/notes/`      | notes |
| `/materials/`  | materials |
| `/deals/`      | generator (Deal pipeline) |
| `/documents/`  | documents |
| `/parts/`      | parts |
| `/assistant/`  | assistant (AI chat) |
| `/calendar/`   | calendar_app (Calendar) |
