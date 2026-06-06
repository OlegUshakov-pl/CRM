![image](image.png)
# CRM

Django 6 + Tailwind CSS 4 + Alpine.js + HTMX + Ollama AI — a project management, contractor and task tracking system for engineering and manufacturing.

## Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Django 6.0, Python 3.14+, SQLite |
| Frontend | Tailwind CSS 4, Alpine.js 3, HTMX 2.0, Lucide Icons |
| AI | Ollama (local LLM), rule-based command processing |
| Font | Montserrat |

## Features

### Core Modules

| Module | Description |
|--------|-------------|
| **Dashboard** | Home page with key metrics, recent projects, tasks and notes |
| **Companies** | Company management (name, email, phone, website, address, logo) |
| **Contacts** | Contacts linked to companies with avatars |
| **Projects** | Projects (statuses, budget, dates, image gallery, ZIP export/import) |
| **Materials / BOM** | Bill of materials per project (quantity, units, prices, categories) |
| **Tasks** | Tasks (priorities, statuses, due dates, filtering) |
| **Notes** | Universal notes linked to projects, companies, contacts |
| **Documents** | File upload with preview (images, PDF, text), filter by type and project |
| **Parts** | Drawings and 3D models (.stp, .ipt, .sldprt, .ics, etc.) |
| **Generator** | Template for rapid module scaffolding (example: Deal pipeline) |

### AI Assistant

#### Ollama Setup

For the AI chat to work, you need to install and run Ollama locally:

1. **Download Ollama** from [ollama.com](https://ollama.com) and install it
2. **Pull a model** (e.g., Llama 3.2, Mistral, or any supported model):
   ```bash
   ollama pull llama3.2
   ```
3. **Start Ollama** (it runs as a background service by default on port 11434)
4. **Select the model** in the CRM chat interface — the dropdown will list all installed models automatically

The model selector appears in the AI Assistant header once Ollama is running. You can switch between models at any time during a conversation.

Built-in AI assistant powered by Ollama with two modes:

- **CHAT** — free conversation with a selected Ollama model
- **COMMANDS** — execute CRM commands via natural language

**Example commands:**
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
```

**Capabilities:**
- Voice input (Web Speech API)
- Browser agent: open URLs, take screenshots, extract titles and PDF links
- AI Files: download files from the web, attach to projects, manage storage
- Undo with a 10-second window for create/delete actions
- All actions logged to AILog
- Model selection from installed Ollama models

### Cross-cutting Features

- Slide-over forms — CRUD without page navigation via HTMX
- Soft delete via `is_active` flag
- Global search across all entity types
- Activity logging with Generic Foreign Key
- Project export/import as ZIP
- Dark mode
- Responsive design

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

The server will be available at `http://127.0.0.1:8000`.

For the AI assistant, a running Ollama instance is required at `http://localhost:11434` (configurable in `settings.py`).

## Project Structure

```
CRM/
├── config/           # Settings, root URLs, WSGI/ASGI
├── accounts/         # Authentication (login, profile, password reset)
├── core/             # Dashboard, TimeStampedModel, Activity, AppSetting, search
├── companies/        # Company management
├── contacts/         # Contact management
├── projects/         # Project management, export/import
├── materials/        # Bill of materials (BOM), categories
├── tasks/            # Task management
├── notes/            # Universal notes
├── documents/        # File management with preview
├── parts/            # Drawings and 3D models
├── assistant/        # AI chat, Ollama, browser, AI Files
│   └── services/     # Command registry, handlers, browser, files, i18n
├── generator/        # Module scaffolding template (Deal pipeline)
├── templates/        # Base layout, includes
│   ├── base.html
│   └── includes/     # sidebar, topbar, chat_widget, pagination, slide_over
├── static/           # Tailwind CSS (src → dist)
│   └── src/styles.css
└── media/            # User uploaded files
```

## Data Models

All models inherit `TimeStampedModel` (created_at, updated_at, created_by, is_active).

| Model | Key Fields |
|-------|-----------|
| Company | name, email, phone, website, address, logo |
| Contact | company (FK), first_name, last_name, email, phone, position, avatar |
| Project | name, number, description, status, company (FK), contacts (M2M), dates, budget, image |
| ProjectImage | project (FK), image, uploaded_at |
| Material | project (FK), category (FK), name, quantity, unit, unit_price, notes |
| Category (materials) | name |
| Task | title, description, status, priority, due_date, project (FK) |
| Note | title, content, date, project (FK), company (FK), contact (FK) |
| Document | project (FK), number, file, file_type, size |
| Part | project (FK), category (FK), number, size, rev, file |
| Category (parts) | name |
| ChatSession | user, title, is_active, last_message_at |
| ChatMessage | session (FK), role, kind, content, payload |
| AIFile | owner (FK), file, original_name, source_url, size, category |
| AILog | user, session (FK), action, status, description, request/response, payload |
| Activity | user, action, description, content_type, object_id (GenericFK) |
| Deal (example) | name, description, status, priority, value, company (FK), contacts (M2M), assigned_to, due_date |
| AppSetting | key, value |

## Development

```bash
# Watch mode for Tailwind CSS
npm run dev

# Production build
npm run build

# Collect Django static files
python manage.py collectstatic
```

## Architecture

- **Slide-over forms** — most CRUD operations use HTMX slide-over panels without page navigation
- **Project file system** — files are organized as `{number}_{name}_Project/{documents,drawings,models}/`
- **AI rules** — intent detection via regex (no NLP model required); all write operations require two-step confirmation
- **Versioning** — app version `1.2.{commit_count}` derived from git commit count
