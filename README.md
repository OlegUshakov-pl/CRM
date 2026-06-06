# CRM

Django 6 + Tailwind CSS 4 + Alpine.js + HTMX + Ollama AI — система управления проектами, контрагентами и задачами для инженерно-производственной сферы.

## Стек

| Слой | Технологии |
|------|-----------|
| Backend | Django 6.0, Python 3.14+, SQLite |
| Frontend | Tailwind CSS 4, Alpine.js 3, HTMX 2.0, Lucide Icons |
| AI | Ollama (локальная LLM), rule-based command processing |
| Шрифт | Montserrat |

## Функциональность

### Основные модули

| Модуль | Описание |
|--------|---------|
| **Dashboard** | Главная страница с ключевыми метриками, последними проектами, задачами и заметками |
| **Companies** | Управление компаниями (название, email, телефон, сайт, адрес, логотип) |
| **Contacts** | Контакты с привязкой к компаниям и аватарами |
| **Projects** | Проекты (статусы, бюджет, даты, галерея изображений, экспорт/импорт ZIP) |
| **Materials / BOM** | Спецификации материалов по проектам (количество, единицы, цены, категории) |
| **Tasks** | Задачи (приоритеты, статусы, сроки, фильтрация) |
| **Notes** | Универсальные заметки с привязкой к проектам, компаниям, контактам |
| **Documents** | Загрузка и просмотр файлов (изображения, PDF, текст), фильтрация по типу и проекту |
| **Parts** | Чертежи и 3D-модели (.stp, .ipt, .sldprt, .ics и др.) |
| **Generator** | Шаблон для быстрого создания новых модулей (пример: Deal pipeline) |

### AI Assistant

Встроенный AI-ассистент на базе Ollama с двумя режимами:

- **CHAT** — свободное общение с выбранной моделью Ollama
- **COMMANDS** — выполнение CRM-команд через естественный язык

**Примеры команд:**
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

**Возможности:**
- Голосовой ввод (Web Speech API)
- Браузер: открытие URL, скриншоты, извлечение заголовков и PDF-ссылок
- AI Files: загрузка файлов из сети, прикрепление к проектам, управление хранилищем
- Откат действий (undo) с окном 10 секунд
- Все действия логируются в AILog
- Выбор модели из списка установленных в Ollama

### Общие возможности

- Slide-over формы — CRUD без перезагрузки страницы через HTMX
- Мягкое удаление (soft delete) через `is_active`
- Глобальный поиск по всем сущностям
- Логирование активности (Activity log с Generic Foreign Key)
- Экспорт/импорт проектов в ZIP
- Темная тема (dark mode)
- Адаптивный интерфейс

## Быстрый старт

```bash
# Клонировать репозиторий
git clone <repo-url> && cd CRM

# Python-зависимости
python -m pip install -r requirements.txt

# Node-зависимости (Tailwind CLI)
npm install

# Собрать Tailwind CSS
npm run build

# Миграции
python manage.py migrate

# Суперпользователь
python manage.py createsuperuser

# Запуск
python manage.py runserver
```

Сервер будет доступен по адресу `http://127.0.0.1:8000`.

Для AI-ассистента требуется запущенный Ollama: `http://localhost:11434` (настраивается в `settings.py`).

## Структура проекта

```
CRM/
├── config/           # Настройки, корневые URLs, WSGI/ASGI
├── accounts/         # Аутентификация (логин, профиль, сброс пароля)
├── core/             # Dashboard, TimeStampedModel, Activity, AppSetting, поиск
├── companies/        # Управление компаниями
├── contacts/         # Управление контактами
├── projects/         # Управление проектами, экспорт/импорт
├── materials/        # Спецификации (BOM), категории
├── tasks/            # Управление задачами
├── notes/            # Универсальные заметки
├── documents/        # Управление файлами с превью
├── parts/            # Чертежи и 3D-модели
├── assistant/        # AI-чат, Ollama, браузер, AI Files
│   └── services/     # Command registry, handlers, browser, files, i18n
├── generator/        # Шаблон для новых модулей (Deal pipeline)
├── templates/        # Базовый layout, инклюды
│   ├── base.html
│   └── includes/     # sidebar, topbar, chat_widget, pagination, slide_over
├── static/           # Tailwind CSS (src → dist)
│   └── src/styles.css
└── media/            # Загруженные пользователем файлы
```

## Модели данных

Все модели наследуют `TimeStampedModel` (created_at, updated_at, created_by, is_active).

| Модель | Ключевые поля |
|--------|--------------|
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

## Разработка

```bash
# Запустить Tailwind в режиме watch
npm run dev

# Или собрать production
npm run build

# Собрать статику Django
python manage.py collectstatic
```

## Архитектурные решения

- **Slide-over формы** — большинство CRUD-операций выполняются в боковой панели через HTMX, без навигации
- **Файловая система проектов** — файлы организованы в структуру `{number}_{name}_Project/{documents,drawings,models}/`
- **Правила для AI** — intent detection через regex (не требует NLP-модели), все write-операции с двухшаговым подтверждением
- **Версионирование** — версия приложения `1.2.{commit_count}` определяется по количеству коммитов git
