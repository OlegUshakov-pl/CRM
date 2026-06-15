# Plan: Settings Page + AI Providers

## Context
CRM uses Django + Tailwind + HTMX + Alpine.js. Settings currently opens as a drawer (slide-over panel) in `base.html`. Need to convert it to a full page at `/settings` with tabs, and add AI provider management.

---

## Step 1 — Create Settings page route and view

**File: `core/urls.py`**
- Add `path('settings/', views.settings_page, name='settings_page')`

**File: `core/views.py`**
- Add `settings_page` view that renders `core/settings.html`
- Move existing `save_setting` and `get_setting` views (keep them for API)

---

## Step 2 — Create Settings page template

**New file: `templates/core/settings.html`**
- Extends `base.html`
- Tab navigation: General | AI | Users
- Uses Alpine.js `x-data` for tab switching and AI provider state
- **General tab**: Current content (Project Storage Path + Subfolder Names) moved from drawer
- **AI tab**: Provider cards grid, API key field, model cards (Phase 1 = static list)
- **Users tab**: Placeholder

---

## Step 3 — Update sidebar

**File: `templates/base.html`**
- Replace the gear icon button in the breadcrumb bar (`onclick="openSettings()"`) with a link to `{% url 'core:settings_page' %}`
- Add a Settings link at the bottom of the sidebar nav (gear icon → `/settings`)

---

## Step 4 — Remove Settings drawer from base.html

**File: `templates/base.html`**
- Remove `#settings-backdrop` and `#settings-panel` elements (lines 317-343)
- Remove `openSettings()`, `closeSettings()`, `loadRootPath()`, `saveSettings()` JS functions
- Keep `getCSRFToken()` (used elsewhere)

---

## Step 5 — AI tab: Provider cards (static, Phase 1)

In `settings.html` Alpine.js data:
- `providers` array with all 8 providers (id, name, type, keyPrefix, keyUrl)
- `selectedProvider`, `apiKey`, `baseUrl`, `keyStatus`, `selectedModel`
- `defaultModels` static JSON from task spec
- Render provider cards in 4-col grid, selected = violet border
- API key field with password toggle, placeholder with prefix, status dot
- For Ollama: show Base URL field instead of key
- "Check Key" button (Phase 1 = just shows green + loads static models)
- Model cards in 3-col grid with badges

---

## Step 6 — Save/load AI config via AppSetting

- Store `ai_provider`, `ai_api_key`, `ai_base_url`, `ai_model` as separate AppSetting keys
- On page load, fetch all settings and populate fields
- Save button validates and saves all tabs' settings

---

## Step 7 — Backend proxy for API key validation (optional/future)

- Add endpoint `POST /settings/ai/check-key/` that proxies request to provider API
- For Phase 1: skip real validation, just mark as "checked"

---

## Files to modify
1. `core/urls.py` — add settings page route
2. `core/views.py` — add settings_page view
3. `templates/base.html` — remove drawer, update sidebar + breadcrumb gear link
4. `templates/core/settings.html` — **new file**, full settings page

## Verification
- Navigate to `/settings` → page loads with General tab active
- Click AI tab → provider cards visible
- Select provider → API key field appears (or Base URL for Ollama)
- Click Save → settings persist in DB
- Sidebar gear icon → navigates to `/settings`
- Old drawer no longer appears
