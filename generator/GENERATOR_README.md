# Generator App — Instructions

This is a **template app** for quickly creating new Django modules in this CRM project.
It contains a complete working example with a `Deal` model and all related files.

## What's Inside

```
generator/
├── __init__.py
├── apps.py                    # App configuration
├── models.py                  # Example model: Deal (with all common field types)
├── forms.py                   # ModelForm with styled widgets
├── views.py                   # CRUD views (list, detail, create, edit, delete, slide-over)
├── urls.py                    # URL patterns (app_name: 'generators')
├── admin.py                   # Admin registration with list_display, filters, search
├── tests.py                   # Empty test file
├── migrations/
│   └── __init__.py
├── templates/generators/
│   ├── deal_list.html          # List view with search, filters, HTMX
│   ├── deal_detail.html        # Detail view with all fields
│   ├── deal_form.html          # Slide-over form (used by HTMX)
│   ├── deal_create_page.html   # Full page create form
│   └── deal_edit_page.html     # Full page edit form
└── GENERATOR_README.md         # This file
```

## How to Use

### Step 1: Copy the generator folder

```bash
cp -r generator your_app_name
```

Or on Windows:
```cmd
xcopy /E /I generator your_app_name
```

### Step 2: Rename the files and references

Replace all occurrences of the following in ALL files:

| Find | Replace with |
|------|-------------|
| `generator` | `your_app_name` (folder name) |
| `generators` | `your_app_name` (in `app_name` and URL namespace) |
| `GeneratorConfig` | `YourAppNameConfig` |
| `Deal` | `YourModelName` |
| `deal` | `your_model_name` (lowercase, for variables and URLs) |
| `DealForm` | `YourModelNameForm` |
| `deal_list` | `your_model_name_list` |
| `deal_detail` | `your_model_name_detail` |
| `deal_create` | `your_model_name_create` |
| `deal_edit` | `your_model_name_edit` |
| `deal_delete` | `your_model_name_delete` |
| `deal_create_slide` | `your_model_name_create_slide` |
| `deal_edit_slide` | `your_model_name_edit_slide` |
| `DealAdmin` | `YourModelNameAdmin` |
| `generators/deal_` | `your_app_name/your_model_name_` (template paths) |
| `your_app_name:detail` | `your_app_name:your_model_name_detail` (if using different URL names) |

### Step 3: Edit models.py

1. Remove fields you don't need
2. Update `STATUS_CHOICES` / `PRIORITY_CHOICES` or remove them
3. Update ForeignKey/M2M relationships (remove if not needed)
4. Update `related_name` to match your app
5. Remove unused imports

**Example — if you don't need Company or Contact relationships:**
```python
# Remove these lines:
from companies.models import Company
from contacts.models import Contact

# And remove from model fields:
# company = models.ForeignKey(Company, ...)
# contacts = models.ManyToManyField(Contact, ...)
```

### Step 4: Edit forms.py

Update the `fields` list in `Meta.fields` to match your model fields.
Update or remove widget configurations for removed fields.

### Step 5: Edit views.py

1. Update imports to match your model and form names
2. Remove views you don't need (e.g., if you don't need slide-over, remove `*_slide` views)
3. Update query optimizations (`select_related`, `prefetch_related`) for your relations
4. Update `log_activity()` calls with your model name

### Step 6: Edit urls.py

Update `app_name` and all URL names. Remove URL patterns you don't need.

### Step 7: Edit admin.py

Update `list_display`, `list_filter`, `search_fields` for your model fields.

### Step 8: Edit templates

1. Rename the templates folder: `templates/generators/` → `templates/your_app_name/`
2. Update all `{% url %}` tags to use your new URL names
3. Update template content (field names, display logic, status/priority badges)
4. Remove sections for fields you don't have
5. Update Lucide icon names if needed

**Key places to update in templates:**
- `{% url 'generators:...' %}` → `{% url 'your_app_name:...' %}`
- `{{ deal.field_name }}` → `{{ your_model.field_name }}`
- Status/priority badge logic (add/remove choices)
- `openSlideOver('{% url '...' %}')` — update slide-over URLs

### Step 9: Register in Django settings

Add your app to `INSTALLED_APPS` in `config/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'your_app_name',
]
```

### Step 10: Register URLs

Add your app URLs to `config/urls.py`:

```python
urlpatterns = [
    ...
    path('your-app-url/', include('your_app_name.urls')),
]
```

### Step 11: Create migrations and run

```bash
python manage.py makemigrations your_app_name
python manage.py migrate
```

### Step 12: (Optional) Add to sidebar

Edit `templates/base.html` and add a link in the `<nav>` section:

```html
<a href="{% url 'your_app_name:list' %}">
    <i data-lucide="your-icon-name" class="w-4 h-4 flex-shrink-0"></i>
    <span class="sidebar-text">Your Module Name</span>
</a>
```

Browse Lucide icons: https://lucide.dev/icons/

## Available URL Names

After setup, these URL names will be available (replace `generators` with your namespace):

| URL Name | Path | Description |
|----------|------|-------------|
| `your_app_name:list` | `/` | List view with search & filters |
| `your_app_name:create` | `/create/` | Full page create form |
| `your_app_name:create_slide` | `/create/slide/` | Slide-over create form |
| `your_app_name:detail` | `/<slug>/` | Detail view |
| `your_app_name:edit` | `/<slug>/edit/` | Full page edit form |
| `your_app_name:edit_slide` | `/<slug>/edit/slide/` | Slide-over edit form |
| `your_app_name:delete` | `/<slug>/delete/` | Soft delete (POST only) |

## Example Workflow

Let's say you want to create an "Invoice" module:

```bash
# 1. Copy
cp -r generator invoices

# 2. Rename 'Deal' to 'Invoice' in all files
# (use your IDE's find & replace)

# 3. Edit models.py — change fields to invoice fields
# 4. Edit forms.py — update fields list
# 5. Edit views.py — update imports and references
# 6. Edit urls.py — change app_name to 'invoices'
# 7. Edit admin.py — update list_display
# 8. Rename templates folder and update template contents

# 9. Add to settings.py
# 'invoices',

# 10. Add to config/urls.py
# path('invoices/', include('invoices.urls')),

# 11. Migrate
python manage.py makemigrations invoices
python manage.py migrate

# 12. Add sidebar link in base.html