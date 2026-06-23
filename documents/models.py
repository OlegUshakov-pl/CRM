import os
from django.db import models
from django.conf import settings
from projects.models import Project
from projects.utils import ProjectFileSystemStorage, sanitize_folder_name, get_subfolder_name


DocumentStorage = ProjectFileSystemStorage

PDF_EXTENSIONS = ('.pdf',)
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')


def get_project_folder_name(project):
    safe_number = sanitize_folder_name(project.number) if project.number else ''
    safe_name = sanitize_folder_name(project.name)
    return f'{safe_number}_{safe_name}_Project'


def get_document_subfolder(project_number, document_type):
    if document_type == 'pdf_catalog':
        return get_subfolder_name(project_number, 'subfolder_pdf_catalog', 'PDF Catalog')
    return get_subfolder_name(project_number, 'subfolder_documents', 'documents')


def document_upload_to(instance, filename):
    if instance.project:
        folder = get_project_folder_name(instance.project)
        doc_type = getattr(instance, 'document_type', None)
        if doc_type == 'pdf_catalog':
            subfolder = get_subfolder_name(instance.project.number, 'subfolder_pdf_catalog', 'PDF Catalog')
        elif doc_type == 'document':
            subfolder = get_subfolder_name(instance.project.number, 'subfolder_documents', 'documents')
        else:
            ext = os.path.splitext(filename)[1].lower()
            if ext in PDF_EXTENSIONS or ext in IMAGE_EXTENSIONS:
                subfolder = get_subfolder_name(instance.project.number, 'subfolder_pdf_catalog', 'PDF Catalog')
            else:
                subfolder = get_subfolder_name(instance.project.number, 'subfolder_documents', 'documents')
        return os.path.join(folder, subfolder, filename)
    return os.path.join('_no_project', filename)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('document', 'Document'),
        ('pdf_catalog', 'PDF Catalog'),
    ]

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', db_index=True)
    number = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    size = models.IntegerField(blank=True, null=True, help_text='File size in bytes')
    file = models.FileField(upload_to=document_upload_to, storage=ProjectFileSystemStorage())
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents', db_index=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='document', db_index=True)
    file_created = models.DateField(blank=True, null=True)
    file_updated = models.DateField(blank=True, null=True)

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
        from projects.utils import get_project_root_path
        root_path = get_project_root_path()
        if root_path and self.file:
            return os.path.join(root_path, self.file.name)
        return os.path.join(settings.MEDIA_ROOT, self.file.name) if self.file else ''

    @property
    def is_pdf(self):
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            return ext in PDF_EXTENSIONS
        return False

    @property
    def is_image(self):
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            return ext in IMAGE_EXTENSIONS
        return False
