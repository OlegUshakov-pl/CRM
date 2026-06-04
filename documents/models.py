import os
from django.db import models
from django.conf import settings
from projects.models import Project
from projects.utils import ProjectFileSystemStorage, sanitize_folder_name


DocumentStorage = ProjectFileSystemStorage


def document_upload_to(instance, filename):
    if instance.project:
        safe_number = sanitize_folder_name(instance.project.number) if instance.project.number else instance.project.slug
        safe_name = sanitize_folder_name(instance.project.name)
        return os.path.join(f'{safe_number}_{safe_name}_Project', f'{safe_number}_documents', filename)
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
        from projects.utils import get_project_subfolder_path
        if self.project:
            safe_number = sanitize_folder_name(self.project.number) if self.project.number else self.project.slug
            folder = get_project_subfolder_path(self.project, f'{safe_number}_documents')
            if folder and self.file:
                return os.path.join(folder, self.filename)
        return os.path.join(settings.DOCUMENTS_ROOT, self.file.name) if self.file else ''
