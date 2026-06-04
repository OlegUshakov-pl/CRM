import os
from django.db import models
from core.models import TimeStampedModel
from projects.models import Project
from projects.utils import ProjectFileSystemStorage, sanitize_folder_name


def part_upload_to(instance, filename):
    if instance.project and instance.project.number:
        safe_number = sanitize_folder_name(instance.project.number)
        safe_name = sanitize_folder_name(instance.project.name)
        ext = os.path.splitext(filename)[1].lower()
        subfolder = f'{safe_number}_models' if ext in Part.MODEL_EXTENSIONS else f'{safe_number}_drawings'
        return os.path.join(f'{safe_number}_{safe_name}_Project', subfolder, filename)
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
