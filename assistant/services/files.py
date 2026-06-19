"""
AI Files service: validate, save, attach, cleanup.
"""
import logging
import os
import uuid
from datetime import timedelta
from typing import List, Optional

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)

CHUNK_SIZE = 64 * 1024  # 64KB chunks for file operations


ALLOWED_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
               '.pdf', '.docx', '.xlsx', '.dwg'}
FORBIDDEN_EXT = {'.exe', '.zip', '.bat', '.cmd', '.msi', '.js'}
CREATE_ALLOWED_EXT = {
    '.txt', '.md', '.csv', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg',
    '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.htm', '.css', '.scss', '.less',
    '.sh', '.rb', '.go', '.rs', '.java', '.kt', '.swift', '.cpp', '.c', '.h',
    '.hpp', '.sql', '.r', '.m', '.mm', '.lua', '.php', '.pl', '.pm', '.vue', '.svelte',
    '.env', '.gitignore', '.dockerfile', '.makefile', '.gradle', '.sln', '.csproj',
    '.drawio', '.svg', '.tex', '.bib', '.log', '.lst',
}


class AIFileService:
    def __init__(self, user):
        self.user = user

    def save_uploaded(self, uploaded_file) -> Optional['AIFile']:
        from ..models import AIFile

        if not uploaded_file:
            return None
        name = uploaded_file.name
        ext = os.path.splitext(name)[1].lower()
        if ext in FORBIDDEN_EXT:
            logger.warning('Rejected forbidden extension: %s', ext)
            return None
        if ext and ext not in ALLOWED_EXT:
            logger.warning('Rejected extension not in allow-list: %s', ext)
            return None

        size = getattr(uploaded_file, 'size', 0)
        if size > settings.AI_FILES_MAX_SIZE:
            logger.warning('File too big: %s', size)
            return None

        ai_file = AIFile(
            owner=self.user,
            original_name=name,
            size=size,
        )
        ai_file.file.save(name, uploaded_file, save=True)
        return ai_file

    def save_downloaded(self, fetch_result) -> Optional['AIFile']:
        from ..models import AIFile
        from io import BytesIO

        if not fetch_result.ok:
            return None
        ext = os.path.splitext(fetch_result.file_name)[1].lower()
        if ext in FORBIDDEN_EXT:
            return None
        if ext and ext not in ALLOWED_EXT:
            return None
        if fetch_result.size > settings.AI_FILES_MAX_SIZE:
            return None

        ai_file = AIFile(
            owner=self.user,
            original_name=fetch_result.file_name,
            source_url=fetch_result.final_url or None,
            size=fetch_result.size,
        )
        content_file = ContentFile(fetch_result.content)
        ai_file.file.save(fetch_result.file_name, content_file, save=True)
        return ai_file

    def save_content(self, filename: str, content: str) -> Optional['AIFile']:
        from ..models import AIFile

        ext = os.path.splitext(filename)[1].lower()
        if ext in FORBIDDEN_EXT:
            logger.warning('Rejected forbidden extension: %s', ext)
            return None
        if ext and ext not in CREATE_ALLOWED_EXT:
            logger.warning('Rejected extension not in create allow-list: %s', ext)
            return None

        size = len(content.encode('utf-8'))
        if size > settings.AI_FILES_MAX_SIZE:
            logger.warning('Content too big: %s', size)
            return None

        ai_file = AIFile(
            owner=self.user,
            original_name=filename,
            size=size,
        )
        ai_file.file.save(filename, ContentFile(content.encode('utf-8')), save=True)
        return ai_file

    def attach_to_project(self, file_id: str, project) -> Optional['Document']:
        from documents.models import Document
        from ..models import AIFile
        try:
            ai = AIFile.objects.get(id=file_id, owner=self.user, is_active=True)
        except AIFile.DoesNotExist:
            return None

        ext = os.path.splitext(ai.original_name)[1].lower()
        if ext in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}:
            file_type = 'photos'
        elif ext == '.pdf':
            file_type = 'documents'
        elif ext in {'.docx', '.xlsx', '.dwg'}:
            file_type = 'documents'
        else:
            file_type = 'other'

        doc = Document(project=project, file_type=file_type, number=ai.original_name, size=ai.size)
        with open(ai.file.path, 'rb') as src:
            doc.file.save(ai.original_name, src, save=True)
        return doc

    def total_size(self) -> int:
        from ..models import AIFile
        total = AIFile.objects.filter(owner=self.user, is_active=True).aggregate(
            s=models.Sum('size')
        )['s'] or 0
        return int(total)

    def cleanup_older_than(self, days: int = 30) -> int:
        from ..models import AIFile
        cutoff = timezone.now() - timedelta(days=days)
        qs = AIFile.objects.filter(created_at__lt=cutoff, is_active=True)
        n = 0
        for f in list(qs):
            try:
                if f.file and os.path.exists(f.file.path):
                    os.remove(f.file.path)
            except OSError:
                pass
            f.is_active = False
            f.save(update_fields=['is_active', 'updated_at'])
            n += 1
        return n
