import os
from django.db import models
from core.models import TimeStampedModel
from projects.models import Project
from projects.utils import ProjectFileSystemStorage, sanitize_folder_name, get_subfolder_name


def part_upload_to(instance, filename):
    if instance.project and instance.project.number:
        ext = os.path.splitext(filename)[1].lower()
        if ext in Part.MODEL_EXTENSIONS:
            subfolder = get_subfolder_name(instance.project.number, 'subfolder_models', 'models')
        else:
            subfolder = get_subfolder_name(instance.project.number, 'subfolder_drawings', 'drawings')
        return os.path.join(subfolder, filename)
    return os.path.join('parts', filename)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Part(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='parts', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='parts')
    number = models.CharField(max_length=255, blank=True)
    size = models.CharField(max_length=255, blank=True, null=True)
    rev = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateField(blank=True, null=True)
    updated = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to=part_upload_to, storage=ProjectFileSystemStorage(), blank=True, null=True)

    MODEL_EXTENSIONS = ['.stp', '.ipt', '.iam', '.sldprt', '.sldasm', '.ics']

    @property
    def is_model(self):
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            return ext in self.MODEL_EXTENSIONS
        return False

    class Meta:
        ordering = ['number']

    def __str__(self):
        return self.number
