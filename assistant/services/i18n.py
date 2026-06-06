"""
Bilingual message templates for the AI assistant.
Detects language from input (presence of cyrillic chars) and picks the
matching message. The chat widget UI itself stays English to match the
rest of the CRM shell.
"""


def detect_lang(text: str) -> str:
    if not text:
        return 'en'
    for ch in text:
        if '\u0400' <= ch <= '\u04FF':
            return 'ru'
    return 'en'


M = {
    # Generic
    'empty': {
        'en': 'Please tell me what to do.',
        'ru': 'Скажите, что нужно сделать.',
    },
    'error_generic': {
        'en': 'Error: {err}',
        'ru': 'Ошибка: {err}',
    },
    'cancelled': {
        'en': 'Action cancelled.',
        'ru': 'Действие отменено.',
    },
    'undo_done': {
        'en': 'Undone.',
        'ru': 'Отменено.',
    },
    'undo_failed': {
        'en': 'Could not undo.',
        'ru': 'Не удалось отменить.',
    },
    'undo_expired': {
        'en': 'Undo window (10 sec) expired.',
        'ru': 'Время отмены (10 сек) истекло.',
    },
    'undo_token_missing': {
        'en': 'No undo token.',
        'ru': 'Нет токена для отмены.',
    },
    'undo_not_found': {
        'en': 'Action not found or already expired.',
        'ru': 'Действие не найдено или уже истекло (10 секунд).',
    },
    'undo_error': {
        'en': 'Could not undo: {err}',
        'ru': 'Не удалось отменить: {err}',
    },
    'clear_confirm': {
        'en': 'Clear chat history?',
        'ru': 'Очистить историю чата?',
    },

    # Create project
    'project_missing_name': {
        'en': 'Project name is required. Try: "Create project [Number], [Name] on [Date]".',
        'ru': 'Не указано название проекта. Скажите: «Создай проект [Номер], [Название] на [Дата]».',
    },
    'project_confirm': {
        'en': 'Create project "{full}" on {date}. Confirm?',
        'ru': 'Создать проект «{full}» на дату {date}. Подтверждаете?',
    },
    'project_done': {
        'en': 'Done. Project "{name}" created.',
        'ru': 'Готово. Создан проект «{name}».',
    },
    'project_open': {
        'en': 'Open', 'ru': 'Открыть',
    },

    # Create task
    'task_missing_title': {
        'en': 'Task text is required. Try: "Add task [Text] on [Date]".',
        'ru': 'Не указан текст задачи. Скажите: «Добавь задачу [Текст] на [Дата]».',
    },
    'task_confirm': {
        'en': 'Create task "{title}" on {date}{project_part}. Confirm?',
        'ru': 'Создать задачу «{title}» на {date}{project_part}. Подтверждаете?',
    },
    'task_project_part': {
        'en': ' in project "{name}"',
        'ru': ' в проекте «{name}»',
    },
    'task_done': {
        'en': 'Done. Task "{title}" created (due: {due}).',
        'ru': 'Готово. Создана задача «{title}» (дедлайн: {due}).',
    },
    'task_open': {
        'en': 'Open tasks', 'ru': 'Открыть задачи',
    },

    # Contact find
    'contact_missing_name': {
        'en': 'Specify a contact name.',
        'ru': 'Укажите имя контакта.',
    },
    'contact_not_found': {
        'en': 'Contact "{name}" not found.',
        'ru': 'Контакт «{name}» не найден.',
    },
    'contact_found': {
        'en': 'Contact: {name}',
        'ru': 'Контакт: {name}',
    },

    # Material add
    'material_missing_name': {
        'en': 'Material name is required.',
        'ru': 'Не указано название материала.',
    },
    'project_not_found': {
        'en': 'Project "{name}" not found.',
        'ru': 'Проект «{name}» не найден.',
    },
    'material_confirm': {
        'en': 'Add material "{name}" ({qty} {unit}) to project "{project}". Confirm?',
        'ru': 'Добавить материал «{name}» ({qty} {unit}) в проект «{project}». Подтверждаете?',
    },
    'material_done': {
        'en': 'Done. Material "{name}" added to project.',
        'ru': 'Готово. Материал «{name}» добавлен в проект.',
    },

    # Document upload
    'doc_confirm': {
        'en': 'Upload file "{file}" to project "{project}" documents. You will need to attach the file in the chat. Continue?',
        'ru': 'Загрузить файл «{file}» в документы проекта «{project}». Файл нужно прикрепить в чате. Продолжить?',
    },

    # Drawings
    'drawings_none': {
        'en': 'No drawings in project "{name}" yet.',
        'ru': 'В проекте «{name}» чертежей пока нет.',
    },
    'drawings_list': {
        'en': 'Drawings of project "{name}" ({count}):',
        'ru': 'Чертежи проекта «{name}» ({count}):',
    },
    'drawings_open_project': {
        'en': 'Open project', 'ru': 'Открыть проект',
    },

    # Company
    'company_missing': {
        'en': 'Project "{name}" has no company assigned.',
        'ru': 'У проекта «{name}» компания не указана.',
    },
    'company_found': {
        'en': 'Company of project "{project}": "{company}".',
        'ru': 'Компания проекта «{project}»: «{company}».',
    },
    'company_open': {
        'en': 'Open', 'ru': 'Открыть',
    },

    # Note
    'note_missing_title': {
        'en': 'Note text is required.',
        'ru': 'Не указан текст заметки.',
    },
    'note_confirm': {
        'en': 'Create note "{title}"{project_part}. Confirm?',
        'ru': 'Создать заметку «{title}»{project_part}. Подтверждаете?',
    },
    'note_project_part': {
        'en': ' for project "{name}"',
        'ru': ' к проекту «{name}»',
    },
    'note_done': {
        'en': 'Done. Note created.',
        'ru': 'Готово. Заметка создана.',
    },

    # Browser
    'browser_missing_url': {
        'en': 'Specify a URL. Example: "Open bbc.com".',
        'ru': 'Укажите URL. Пример: «Открой bbc.com».',
    },
    'browser_fetch_error': {
        'en': 'Failed to open: {err}',
        'ru': 'Не удалось открыть: {err}',
    },
    'browser_open_error': {
        'en': 'Failed to open the site.',
        'ru': 'Не удалось открыть сайт.',
    },
    'browser_done': {
        'en': 'Opening {url}. Found {titles} title(s).{pdfs}',
        'ru': 'Открываю {url}. Найдено заголовков: {titles}.{pdfs}',
    },
    'browser_pdf_part': {
        'en': ' PDF links: {n}.',
        'ru': ' PDF-ссылок: {n}.',
    },
    'browser_open_new_tab': {
        'en': 'Open in new tab', 'ru': 'Открыть в новой вкладке',
    },

    # Download file
    'download_missing_url': {
        'en': 'Specify a URL. Example: "Download image from https://…".',
        'ru': 'Укажите URL. Пример: «Скачай картинку с https://…».',
    },
    'download_error': {
        'en': 'Failed to download: {err}',
        'ru': 'Не удалось скачать: {err}',
    },
    'download_failed': {
        'en': 'Failed to download the file.',
        'ru': 'Не удалось скачать файл.',
    },
    'download_blocked': {
        'en': 'File failed the security check (type or size).',
        'ru': 'Файл не прошёл проверку безопасности (тип/размер).',
    },
    'download_done': {
        'en': 'Done. File "{name}" in AI Files ({size} bytes). Attach to project?',
        'ru': 'Готово. Файл «{name}» в AI Files ({size} байт). Прикрепить к проекту?',
    },
    'download_attach_action': {
        'en': 'Attach to project', 'ru': 'Прикрепить к проекту',
    },

    # QA
    'qa_tasks': {
        'en': 'Active tasks: {n}.',
        'ru': 'Сейчас активных задач: {n}.',
    },
    'qa_projects_active': {
        'en': 'Active projects: {n}.',
        'ru': 'Активных проектов: {n}.',
    },
    'qa_companies': {
        'en': 'Companies: {n}.', 'ru': 'Компаний: {n}.',
    },
    'qa_contacts': {
        'en': 'Contacts: {n}.', 'ru': 'Контактов: {n}.',
    },
    'qa_documents_none': {
        'en': 'No documents yet.', 'ru': 'Документов пока нет.',
    },
    'qa_documents_last': {
        'en': 'Latest document: "{name}" (project: {project}).',
        'ru': 'Последний документ: «{name}» (проект: {project}).',
    },
    'qa_documents_no_project': {
        'en': 'no project', 'ru': 'без проекта',
    },
    'qa_tasks_none': {
        'en': 'No tasks yet.', 'ru': 'Задач пока нет.',
    },
    'qa_tasks_last': {
        'en': 'Latest task: "{title}" (status: {status}).',
        'ru': 'Последняя задача: «{title}» (статус: {status}).',
    },
    'qa_projects_none': {
        'en': 'No projects yet.', 'ru': 'Проектов пока нет.',
    },
    'qa_projects_last': {
        'en': 'Latest project: "{name}" (status: {status}).',
        'ru': 'Последний проект: «{name}» (статус: {status}).',
    },
    'qa_how_to_material': {
        'en': 'Open "Materials" in the sidebar → "Project Materials" → pick a project → click "+ Add Material" (or just tell me: "Add material … to project …").',
        'ru': 'Откройте «Materials» в боковом меню → «Project Materials» → выберите проект → кнопка «+ Add Material» (или скажите мне: «Добавь материал … в проект …»).',
    },
    'qa_how_to_project': {
        'en': 'Open "Projects" in the sidebar, click "+ Add Project", fill the fields and save. Or tell me: "Create project [Number], [Name] on [Date]".',
        'ru': 'В меню «Projects» нажмите «+ Add Project», заполните поля и сохраните. Или скажите мне: «Создай проект [Номер], [Название] на [Дата]».',
    },
    'qa_how_to_upload': {
        'en': 'Open the project, go to "Documents" tab → "Upload", choose a file. Or tell me: "Upload file [name] to project documents of [Project name]" (you will need to attach the file in chat).',
        'ru': 'В карточке проекта откройте вкладку «Documents» → «Upload», выберите файл. Или скажите: «Загрузи файл [имя] в документы проекта [Название]» (файл нужно прикрепить в чате).',
    },

    # Default fallback
    'no_executor': {
        'en': 'No executor for {intent}.',
        'ru': 'Нет исполнителя для {intent}.',
    },
    'no_pending': {
        'en': 'No pending action to confirm.',
        'ru': 'Нет отложенного действия для подтверждения.',
    },
    'no_intent': {
        'en': 'No intent found for confirmation.',
        'ru': 'Не найден intent для подтверждения.',
    },
    'bad_json': {
        'en': 'Invalid JSON.', 'ru': 'Неверный JSON.',
    },
    'empty_message': {
        'en': 'Empty message.', 'ru': 'Пустое сообщение.',
    },
    'file_rejected': {
        'en': 'File rejected (type or size).',
        'ru': 'Файл отклонён (тип или размер).',
    },
    'file_not_found': {
        'en': 'File not found.', 'ru': 'Файл не найден.',
    },
    'project_id_missing': {
        'en': 'Project is required.', 'ru': 'Не указан проект.',
    },
    'attach_failed': {
        'en': 'Could not attach.', 'ru': 'Не удалось прикрепить.',
    },
    'attached': {
        'en': 'Attached', 'ru': 'Прикреплено',
    },
    'select_project': {
        'en': 'Choose a project', 'ru': 'Выберите проект',
    },
    'no_files_selected': {
        'en': 'No files selected.', 'ru': 'Не выбраны файлы.',
    },
    'confirm_delete_file': {
        'en': 'Delete the file?', 'ru': 'Удалить файл?',
    },
    'confirm_bulk_delete': {
        'en': 'Delete selected files?', 'ru': 'Удалить выбранные файлы?',
    },
    'confirm_cleanup': {
        'en': 'Delete all AI Files older than 30 days?',
        'ru': 'Удалить все AI Files старше 30 дней?',
    },
    'voice_tooltip': {
        'en': 'Voice control will be added in the next release (v2).',
        'ru': 'Голосовое управление будет добавлено в следующем обновлении (v2).',
    },
    'mic_title': {
        'en': 'Voice (coming soon)', 'ru': 'Голос скоро',
    },
    'undo_label': {
        'en': 'Undo', 'ru': 'Отменить',
    },
    's_unit': {
        'en': 's', 'ru': 'с',
    },
    'preview_label': {
        'en': 'Preview: ', 'ru': 'Просмотр: ',
    },
    'thinking': {
        'en': 'Thinking...', 'ru': 'Думаю...',
    },
    'executing': {
        'en': 'Executing...', 'ru': 'Выполняю...',
    },
    'confirm_btn': {
        'en': 'Confirm', 'ru': 'Подтвердить',
    },
    'cancel_btn': {
        'en': 'Cancel', 'ru': 'Отмена',
    },
    'chat_placeholder': {
        'en': 'What to do?', 'ru': 'Что сделать?',
    },
    'voice_note': {
        'en': 'Voice control will be added in the next release.',
        'ru': 'Голосовое управление будет добавлено в следующем обновлении.',
    },
    'assistant_title': {
        'en': 'AI Assistant', 'ru': 'AI Ассистент',
    },
    'storage_info': {
        'en': 'AI Files: {used} / {total} ({pct}%)',
        'ru': 'AI Files: {used} / {total} ({pct}%)',
    },
    'success': {
        'en': 'Success', 'ru': 'Успех',
    },
    'no_files': {
        'en': 'No files.', 'ru': 'Нет файлов.',
    },
}


def t(key: str, lang: str = 'en', **kwargs) -> str:
    entry = M.get(key)
    if not entry:
        return key
    text = entry.get(lang) or entry.get('en') or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
