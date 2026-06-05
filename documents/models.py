import os
from django.db import models
from django.conf import settings
from projects.models import Project
from projects.utils import ProjectFileSystemStorage, sanitize_folder_name, get_subfolder_name


DocumentStorage = ProjectFileSystemStorage


def document_upload_to(instance, filename):
    if instance.project:
        file_type = getattr(instance, 'file_type', 'other')
        subfolder_map = {
            'drawings': get_subfolder_name(instance.project.number, 'subfolder_drawings', 'drawings'),
            'models_3d': get_subfolder_name(instance.project.number, 'subfolder_models', 'models'),
            'documents': get_subfolder_name(instance.project.number, 'subfolder_documents', 'documents'),
            'photos': get_subfolder_name(instance.project.number, 'subfolder_documents', 'documents'),
            'other': get_subfolder_name(instance.project.number, 'subfolder_documents', 'documents'),
        }
        subfolder = subfolder_map.get(file_type, get_subfolder_name(instance.project.number, 'subfolder_documents', 'documents'))
        return os.path.join(subfolder, filename)
    return os.path.join('_no_project', filename)


class Document(models.Model):
    FILE_TYPE_CHOICES = [
        ('drawings', 'Drawings'),
        ('models_3d', 'Models 3D'),
        ('documents', 'Documents'),
        ('photos', 'Photos'),
        ('other', 'Other'),
    ]

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    size = models.IntegerField(blank=True, null=True, help_text='File size in bytes')
    file = models.FileField(upload_to=document_upload_to, storage=ProjectFileSystemStorage(fallback=str(settings.DOCUMENTS_ROOT)))
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, default='other')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        project_name = self.project.name if self.project else 'No Project'
        return f"{self.number or self.file.name} - {project_name}"

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
        from core.models import AppSetting
        root_path = AppSetting.get_value('project_root_path', '')
        if root_path and self.file:
            return os.path.join(root_path, self.file.name)
        return os.path.join(settings.DOCUMENTS_ROOT, self.file.name) if self.file else ''
