import os
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from projects.models import Project


class DocumentStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=settings.DOCUMENTS_ROOT)


def document_upload_to(instance, filename):
    return os.path.join(instance.project.slug, instance.file_type, filename)


class Document(models.Model):
    FILE_TYPE_CHOICES = [
        ('contracts', 'Contracts'),
        ('reports', 'Reports'),
        ('drawings', 'Drawings'),
        ('photos', 'Photos'),
        ('invoices', 'Invoices'),
        ('other', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    size = models.IntegerField(blank=True, null=True, help_text='File size in bytes')
    file = models.FileField(upload_to=document_upload_to, storage=DocumentStorage())
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, default='other')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.number or self.file.name} - {self.project.name}"

    def save(self, *args, **kwargs):
        if self.file and not self.size:
            try:
                self.size = self.file.size
            except Exception:
                pass
        super().save(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else ''

    @property
    def filepath(self):
        return os.path.join(settings.DOCUMENTS_ROOT, self.file.name) if self.file else ''
