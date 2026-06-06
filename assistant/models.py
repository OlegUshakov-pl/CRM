import os
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel
from projects.utils import ProjectFileSystemStorage


def ai_file_upload_to(instance, filename):
    user_dir = f'user_{instance.owner_id}' if instance.owner_id else 'shared'
    return os.path.join(user_dir, filename)


class ChatSession(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chat_sessions')
    title = models.CharField(max_length=255, blank=True, default='')
    is_active = models.BooleanField(default=True)
    last_message_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-last_message_at']

    def __str__(self):
        return f'{self.user.username}: {self.title or "Chat"}'


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    KIND_CHOICES = [
        ('text', 'Text'),
        ('confirmation', 'Confirmation'),
        ('result', 'Result'),
        ('undo', 'Undo'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='text')
    content = models.TextField()
    payload = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        snippet = (self.content[:40] + '...') if len(self.content) > 40 else self.content
        return f'[{self.role}] {snippet}'


class AIFile(TimeStampedModel):
    CATEGORY_CHOICES = [
        ('image', 'Image'),
        ('pdf', 'PDF'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_files')
    file = models.FileField(upload_to=ai_file_upload_to, storage=ProjectFileSystemStorage())
    original_name = models.CharField(max_length=255)
    source_url = models.URLField(blank=True, null=True)
    size = models.PositiveBigIntegerField(default=0)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.original_name

    def save(self, *args, **kwargs):
        if self.file and not self.size:
            try:
                self.size = self.file.size
            except Exception:
                pass
        if not self.category and self.original_name:
            ext = os.path.splitext(self.original_name)[1].lower()
            if ext in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}:
                self.category = 'image'
            elif ext == '.pdf':
                self.category = 'pdf'
            elif ext in {'.doc', '.docx', '.xls', '.xlsx', '.txt', '.csv'}:
                self.category = 'document'
        super().save(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else self.original_name


class AILog(TimeStampedModel):
    ACTION_CHOICES = [
        ('chat', 'Chat Message'),
        ('action', 'CRM Action'),
        ('browser', 'Browser Action'),
        ('file', 'File Operation'),
        ('undo', 'Undo'),
    ]
    STATUS_CHOICES = [
        ('ok', 'OK'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_logs')
    session = models.ForeignKey(ChatSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ok')
    description = models.CharField(max_length=512)
    request_text = models.TextField(blank=True, null=True)
    response_text = models.TextField(blank=True, null=True)
    payload = models.JSONField(blank=True, null=True)
    duration_ms = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Log'
        verbose_name_plural = 'AI Logs'

    def __str__(self):
        return f'{self.user} • {self.action} • {self.description[:60]}'
