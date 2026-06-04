from django.db import models
from core.models import TimeStampedModel
from projects.models import Project


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
    number = models.CharField(max_length=255)
    size = models.CharField(max_length=255, blank=True, null=True)
    rev = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateField(blank=True, null=True)
    updated = models.DateField(blank=True, null=True)
    file = models.FileField(upload_to='parts/', blank=True, null=True)

    MODEL_EXTENSIONS = ['.stp', '.ipt', '.iam', '.sldprt', '.sldasm', '.ics']

    @property
    def is_model(self):
        if self.file:
            import os
            ext = os.path.splitext(self.file.name)[1].lower()
            return ext in self.MODEL_EXTENSIONS
        return False

    class Meta:
        ordering = ['number']

    def __str__(self):
        return self.number
