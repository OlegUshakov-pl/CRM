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
    )

    def __init__(self):
        self.registry = command_registry
        if not self.registry._handlers:  # noqa: SLF001
            _handlers.register_all(self.registry)

    def process(self, text: str, user: Any, session: Any = None, model: str = '') -> Dict[str, Any]:
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
                model=model,
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

        return self._ok(t('no_understand', lang), duration_ms=duration_ms, kind='text', lang=lang)

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

        if 'how many' in low:
            if 'task' in low:
                n = Task.objects.filter(is_active=True).count()
                return t('qa_tasks', lang, n=n)
            if 'project' in low:
                n = Project.objects.filter(is_active=True, status='active').count()
                return t('qa_projects_active', lang, n=n)
            if 'company' in low or 'companies' in low:
                c = Company.objects.filter(is_active=True).count()
                return t('qa_companies', lang, n=c)
            if 'contact' in low:
                ct = Contact.objects.filter(is_active=True).count()
                return t('qa_contacts', lang, n=ct)

        if 'latest' in low or 'last' in low:
            if 'document' in low:
                doc = Document.objects.order_by('-created_at').first()
                if not doc:
                    return t('qa_documents_none', lang)
                proj = doc.project.name if doc.project else t('qa_documents_no_project', lang)
                return t('qa_documents_last', lang, name=doc.filename, project=proj)

            if 'task' in low:
                tk = Task.objects.filter(is_active=True).order_by('-created_at').first()
                if not tk:
                    return t('qa_tasks_none', lang)
                return t('qa_tasks_last', lang, title=tk.title, status=tk.get_status_display())

            if 'project' in low:
                p = Project.objects.filter(is_active=True).order_by('-created_at').first()
                if not p:
                    return t('qa_projects_none', lang)
                return t('qa_projects_last', lang, name=p.name, status=p.get_status_display())

        if 'how to add material' in low:
            return t('qa_how_to_material', lang)
        if 'how to create project' in low:
            return t('qa_how_to_project', lang)
        if 'how to upload' in low:
            return t('qa_how_to_upload', lang)

        if 'command' in low and ('can you' in low or 'help' in low or 'what can' in low):
            return t('see_help_page', lang)

        return None

    def _call_remote_llm(self, text: str, user: Any) -> Optional[Dict[str, Any]]:
        return None
