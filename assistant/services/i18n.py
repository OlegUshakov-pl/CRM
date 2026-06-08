"""
English-only message templates for the AI assistant.
"""


def detect_lang(text: str) -> str:
    return 'en'


M = {
    # Generic
    'empty': {
        'en': 'Please tell me what to do.',
    },
    'error_generic': {
        'en': 'Error: {err}',
    },
    'cancelled': {
        'en': 'Action cancelled.',
    },
    'undo_done': {
        'en': 'Undone.',
    },
    'undo_failed': {
        'en': 'Could not undo.',
    },
    'undo_expired': {
        'en': 'Undo window (10 sec) expired.',
    },
    'undo_token_missing': {
        'en': 'No undo token.',
    },
    'undo_not_found': {
        'en': 'Action not found or already expired.',
    },
    'undo_error': {
        'en': 'Could not undo: {err}',
    },
    'clear_confirm': {
        'en': 'Clear chat history?',
    },

    # Create project
    'project_missing_name': {
        'en': 'Project name is required. Try: "Create project [Number], [Name] on [Date]".',
    },
    'project_confirm': {
        'en': 'Create project "{full}" on {date}. Confirm?',
    },
    'project_done': {
        'en': 'Done. Project "{name}" created.',
    },
    'project_open': {
        'en': 'Open',
    },

    # Create task
    'task_missing_title': {
        'en': 'Task text is required. Try: "Add task [Text] on [Date]".',
    },
    'task_confirm': {
        'en': 'Create task "{title}" on {date}{project_part}. Confirm?',
    },
    'task_project_part': {
        'en': ' in project "{name}"',
    },
    'task_done': {
        'en': 'Done. Task "{title}" created (due: {due}).',
    },
    'task_open': {
        'en': 'Open tasks',
    },

    # Contact find
    'contact_missing_name': {
        'en': 'Specify a contact name.',
    },
    'contact_not_found': {
        'en': 'Contact "{name}" not found.',
    },
    'contact_found': {
        'en': 'Contact: {name}',
    },

    # Material add
    'material_missing_name': {
        'en': 'Material name is required.',
    },
    'project_not_found': {
        'en': 'Project "{name}" not found.',
    },
    'material_confirm': {
        'en': 'Add material "{name}" ({qty} {unit}) to project "{project}". Confirm?',
    },
    'material_done': {
        'en': 'Done. Material "{name}" added to project.',
    },

    # Document upload
    'doc_confirm': {
        'en': 'Upload file "{file}" to project "{project}" documents. You will need to attach the file in the chat. Continue?',
    },

    # Drawings
    'drawings_none': {
        'en': 'No drawings in project "{name}" yet.',
    },
    'drawings_list': {
        'en': 'Drawings of project "{name}" ({count}):',
    },
    'drawings_open_project': {
        'en': 'Open project',
    },

    # Company
    'company_missing': {
        'en': 'Project "{name}" has no company assigned.',
    },
    'company_found': {
        'en': 'Company of project "{project}": "{company}".',
    },
    'company_open': {
        'en': 'Open',
    },

    # Note
    'note_missing_title': {
        'en': 'Note text is required.',
    },
    'note_confirm': {
        'en': 'Create note "{title}"{project_part}. Confirm?',
    },
    'note_project_part': {
        'en': ' for project "{name}"',
    },
    'note_done': {
        'en': 'Done. Note created.',
    },

    # Browser
    'browser_missing_url': {
        'en': 'Specify a URL. Example: "Open bbc.com".',
    },
    'browser_fetch_error': {
        'en': 'Failed to open: {err}',
    },
    'browser_open_error': {
        'en': 'Failed to open the site.',
    },
    'browser_done': {
        'en': 'Opening {url}. Found {titles} title(s).{pdfs}',
    },
    'browser_pdf_part': {
        'en': ' PDF links: {n}.',
    },
    'browser_open_new_tab': {
        'en': 'Open in new tab',
    },

    # Download file
    'download_missing_url': {
        'en': 'Specify a URL. Example: "Download image from https://...".',
    },
    'download_error': {
        'en': 'Failed to download: {err}',
    },
    'download_failed': {
        'en': 'Failed to download the file.',
    },
    'download_blocked': {
        'en': 'File failed the security check (type or size).',
    },
    'download_done': {
        'en': 'Done. File "{name}" in AI Files ({size} bytes). Attach to project?',
    },
    'download_attach_action': {
        'en': 'Attach to project',
    },

    # Web search
    'search_missing_query': {
        'en': 'Specify what to search for. Example: "Search for latest Python news".',
    },
    'search_failed': {
        'en': 'Web search failed: {err}',
    },
    'search_no_results': {
        'en': 'No results found for "{query}".',
    },
    'search_done': {
        'en': 'Found {count} result(s) for "{query}":',
    },

    # Find on site
    'find_on_site_missing_params': {
        'en': 'Specify file type (pdf/picture) and site URL. Example: "Find pdf on site https://example.com".',
    },
    'find_on_site_fetch_error': {
        'en': 'Failed to open site: {err}',
    },
    'find_on_site_not_html': {
        'en': 'The URL does not contain HTML content.',
    },
    'find_on_site_none': {
        'en': 'No {type} found on {site}.',
    },
    'find_on_site_done': {
        'en': 'Found {count} {type} on {site}:',
    },

    # Create file
    'file_create_missing_name': {
        'en': 'Specify a filename. Try: "Create file hello.py with content ...".',
    },
    'file_create_missing_content': {
        'en': 'Provide content for the file, or a description so the AI can generate it.',
    },
    'file_create_rejected': {
        'en': 'File type not allowed or content too large.',
    },
    'file_create_generation_failed': {
        'en': 'AI content generation failed: {err}',
    },
    'file_create_done': {
        'en': 'Done. File "{name}" created in AI Files ({size} bytes). Attach to project?',
    },

    # QA
    'qa_tasks': {
        'en': 'Active tasks: {n}.',
    },
    'qa_projects_active': {
        'en': 'Active projects: {n}.',
    },
    'qa_companies': {
        'en': 'Companies: {n}.',
    },
    'qa_contacts': {
        'en': 'Contacts: {n}.',
    },
    'qa_documents_none': {
        'en': 'No documents yet.',
    },
    'qa_documents_last': {
        'en': 'Latest document: "{name}" (project: {project}).',
    },
    'qa_documents_no_project': {
        'en': 'no project',
    },
    'qa_tasks_none': {
        'en': 'No tasks yet.',
    },
    'qa_tasks_last': {
        'en': 'Latest task: "{title}" (status: {status}).',
    },
    'qa_projects_none': {
        'en': 'No projects yet.',
    },
    'qa_projects_last': {
        'en': 'Latest project: "{name}" (status: {status}).',
    },
    'qa_how_to_material': {
        'en': 'Open "Materials" in the sidebar -> "Project Materials" -> pick a project -> click "+ Add Material" (or just tell me: "Add material ... to project ...").',
    },
    'qa_how_to_project': {
        'en': 'Open "Projects" in the sidebar, click "+ Add Project", fill the fields and save. Or tell me: "Create project [Number], [Name] on [Date]".',
    },
    'qa_how_to_upload': {
        'en': 'Open the project, go to "Documents" tab -> "Upload", choose a file. Or tell me: "Upload file [name] to project documents of [Project name]" (you will need to attach the file in chat).',
    },

    # Default fallback
    'no_executor': {
        'en': 'No executor for {intent}.',
    },
    'no_pending': {
        'en': 'No pending action to confirm.',
    },
    'no_intent': {
        'en': 'No intent found for confirmation.',
    },
    'bad_json': {
        'en': 'Invalid JSON.',
    },
    'empty_message': {
        'en': 'Empty message.',
    },
    'no_understand': {
        'en': "I don't understand. Try rephrasing or check the HELP page.",
    },
    'see_help_page': {
        'en': 'Open the HELP page in the top-right corner to see all available commands.',
    },
    'file_rejected': {
        'en': 'File rejected (type or size).',
    },
    'file_not_found': {
        'en': 'File not found.',
    },
    'project_id_missing': {
        'en': 'Project is required.',
    },
    'attach_failed': {
        'en': 'Could not attach.',
    },
    'attached': {
        'en': 'Attached',
    },
    'select_project': {
        'en': 'Choose a project',
    },
    'no_files_selected': {
        'en': 'No files selected.',
    },
    'confirm_delete_file': {
        'en': 'Delete the file?',
    },
    'confirm_bulk_delete': {
        'en': 'Delete selected files?',
    },
    'confirm_cleanup': {
        'en': 'Delete all AI Files older than 30 days?',
    },
    'voice_tooltip': {
        'en': 'Voice control will be added in the next release (v2).',
    },
    'mic_title': {
        'en': 'Voice (coming soon)',
    },
    'undo_label': {
        'en': 'Undo',
    },
    's_unit': {
        'en': 's',
    },
    'preview_label': {
        'en': 'Preview: ',
    },
    'thinking': {
        'en': 'Thinking...',
    },
    'executing': {
        'en': 'Executing...',
    },
    'confirm_btn': {
        'en': 'Confirm',
    },
    'cancel_btn': {
        'en': 'Cancel',
    },
    'chat_placeholder': {
        'en': 'What are you looking for?',
    },
    'voice_note': {
        'en': 'Voice control will be added in the next release.',
    },
    'assistant_title': {
        'en': 'AI Assistant',
    },
    'storage_info': {
        'en': 'AI Files: {used} / {total} ({pct}%)',
    },
    'success': {
        'en': 'Success',
    },
    'no_files': {
        'en': 'No files.',
    },
}


def t(key: str, lang: str = 'en', **kwargs) -> str:
    entry = M.get(key)
    if not entry:
        return key
    text = entry.get('en') or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
