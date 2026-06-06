import re
import time
from typing import Any, Dict, List, Optional, Tuple

from .commands import CommandContext, CommandResult, command_registry
from . import handlers as _handlers
from .i18n import detect_lang, t


class LLMService:
    """
    Rule-based LLM facade.

    Responsibilities:
    - Intent detection via regex patterns registered in `command_registry`.
    - Param extraction (dates, quantities, etc.).
    - Fallback Q&A on CRM data when the user asks a question rather than a command.
    - A clean seam (`_call_remote_llm`) for swapping in a real local LLM later.
    """

    QUESTION_HINTS = (
        'how many', 'show', 'list', 'find', 'where', 'what', 'which', 'when',
        'why', 'how to', 'help', 'tell me', 'explain', 'is there', 'are there',
        'сколько', 'какие', 'какой', 'какая', 'когда', 'почему', 'зачем',
        'что', 'где', 'кто', 'есть ли', 'покажи', 'расскажи',
        'как', 'можно ли', 'помоги', 'объясни',
    )

    def __init__(self):
        self.registry = command_registry
        if not self.registry._handlers:  # noqa: SLF001
            _handlers.register_all(self.registry)

    def process(self, text: str, user: Any, session: Any = None) -> Dict[str, Any]:
        start = time.time()
        text = (text or '').strip()
        lang = detect_lang(text)
        if not text:
            return self._ok(t('empty', lang), duration_ms=0, kind='text', lang=lang)

        intent = self.registry.match(text)
        if intent:
            params = self._extract_params_for_intent(intent, text)
            params['lang'] = lang
            ctx = CommandContext(
                user=user,
                text=text,
                intent=intent,
                params=params,
                session=session,
            )
            result = self.registry.handle(intent, ctx)
            duration_ms = int((time.time() - start) * 1000)
            return {
                'kind': 'command',
                'intent': intent,
                'duration_ms': duration_ms,
                'lang': lang,
                **result.to_dict(),
            }

        qa_answer = self._answer_question(text, user, lang)
        duration_ms = int((time.time() - start) * 1000)
        if qa_answer:
            return self._ok(qa_answer, duration_ms=duration_ms, kind='qa', lang=lang)

        help_text = self._help_text(lang)
        return self._ok(help_text, duration_ms=duration_ms, kind='help', lang=lang)

    def _extract_params_for_intent(self, intent: str, text: str) -> Dict[str, Any]:
        for pattern, matched_intent in self.registry._patterns:  # noqa: SLF001
            if matched_intent != intent:
                continue
            m = pattern.search(text)
            if m:
                return self.registry.extract_params(text, m.groupdict())
        return {}

    def _ok(self, message: str, duration_ms: int = 0, kind: str = 'text', lang: str = 'en', **extra) -> Dict[str, Any]:
        return {
            'kind': kind,
            'duration_ms': duration_ms,
            'lang': lang,
            'ok': True,
            'message': message,
            'needs_confirmation': False,
            'confirmation_text': '',
            'payload': {},
            'actions': [],
            'undoable': False,
            'undo_token': None,
            'error': '',
            **extra,
        }

    def _answer_question(self, text: str, user: Any, lang: str) -> Optional[str]:
        low = text.lower()
        if not any(h in low for h in self.QUESTION_HINTS):
            return None

        from projects.models import Project
        from tasks.models import Task
        from companies.models import Company
        from contacts.models import Contact
        from notes.models import Note
        from materials.models import Material
        from documents.models import Document
        from parts.models import Part

        if 'сколько' in low or 'how many' in low:
            if 'задач' in low or 'task' in low:
                n = Task.objects.filter(is_active=True).count()
                return t('qa_tasks', lang, n=n)
            if 'проект' in low or 'project' in low:
                n = Project.objects.filter(is_active=True, status='active').count()
                return t('qa_projects_active', lang, n=n)
            if 'компан' in low or 'company' in low or 'companies' in low:
                c = Company.objects.filter(is_active=True).count()
                return t('qa_companies', lang, n=c)
            if 'контакт' in low or 'contact' in low:
                ct = Contact.objects.filter(is_active=True).count()
                return t('qa_contacts', lang, n=ct)

        if ('последн' in low or 'latest' in low or 'last' in low):
            if 'документ' in low or 'document' in low:
                doc = Document.objects.order_by('-created_at').first()
                if not doc:
                    return t('qa_documents_none', lang)
                proj = doc.project.name if doc.project else t('qa_documents_no_project', lang)
                return t('qa_documents_last', lang, name=doc.filename, project=proj)

            if 'задач' in low or 'task' in low:
                tk = Task.objects.filter(is_active=True).order_by('-created_at').first()
                if not tk:
                    return t('qa_tasks_none', lang)
                return t('qa_tasks_last', lang, title=tk.title, status=tk.get_status_display())

            if 'проект' in low or 'project' in low:
                p = Project.objects.filter(is_active=True).order_by('-created_at').first()
                if not p:
                    return t('qa_projects_none', lang)
                return t('qa_projects_last', lang, name=p.name, status=p.get_status_display())

        if 'как добавить материал' in low or 'how to add material' in low or ('материал' in low and 'как' in low):
            return t('qa_how_to_material', lang)
        if 'как создать проект' in low or 'how to create project' in low or ('проект' in low and 'создать' in low and 'как' in low):
            return t('qa_how_to_project', lang)
        if 'как загрузить файл' in low or 'how to upload' in low or ('загрузить' in low and 'файл' in low and 'как' in low):
            return t('qa_how_to_upload', lang)

        if ('команд' in low and ('умеешь' in low or 'можешь' in low or 'что ты' in low)) or \
           ('command' in low and ('can you' in low or 'help' in low or 'what can' in low)):
            return self._help_text(lang)

        return None

    def _help_text(self, lang: str) -> str:
        if lang == 'ru':
            return (
                'Я умею:\n'
                '• Создавать проекты: «Создай проект 001, Тест на завтра»\n'
                '• Добавлять задачи: «Добавь задачу Позвонить клиенту на завтра»\n'
                '• Искать контакты: «Найди контакт Иван»\n'
                '• Добавлять материалы: «Добавь материал Болт 50 в проект Тест»\n'
                '• Загружать документы: «Загрузи файл чертёж.pdf в документы проекта Тест»\n'
                '• Показывать чертежи: «Покажи все чертежи по проекту Тест»\n'
                '• Показывать компанию: «Какая компания у проекта Тест»\n'
                '• Создавать заметки: «Создай заметку Встреча к проекту Тест»\n'
                '• Отвечать на вопросы: «Сколько активных задач?», «Покажи последний документ».\n\n'
                'Голос появится в v2. Скажите, что нужно сделать.'
            )
        return (
            'I can:\n'
            '• Create projects: "Create project 001, Test tomorrow"\n'
            '• Add tasks: "Add task Call client tomorrow"\n'
            '• Find contacts: "Find contact Ivan"\n'
            '• Add materials: "Add material Bolt 50 to project Test"\n'
            '• Upload documents: "Upload file drawing.pdf to project Test documents"\n'
            '• Show drawings: "Show all drawings of project Test"\n'
            '• Show company: "What is the company of project Test"\n'
            '• Create notes: "Create note Meeting for project Test"\n'
            '• Answer questions: "How many active tasks?", "Show the latest document".\n\n'
            'Voice is coming in v2. Just tell me what to do.'
        )

    def _call_remote_llm(self, text: str, user: Any) -> Optional[Dict[str, Any]]:
        return None
