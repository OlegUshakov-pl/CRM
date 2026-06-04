import os
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from core.models import TimeStampedModel, generate_unique_slug
from companies.models import Company
from contacts.models import Contact
from .utils import sanitize_folder_name


def project_image_upload_to(instance, filename):
    if instance.project and instance.project.number:
        safe_number = sanitize_folder_name(instance.project.number)
        safe_name = sanitize_folder_name(instance.project.name)
        return os.path.join(f'{safe_number}_{safe_name}_Project', f'{safe_number}_documents', filename)
    return os.path.join('projects', filename)


class Project(TimeStampedModel):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    contacts = models.ManyToManyField(Contact, blank=True, related_name='projects')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    number = models.CharField(max_length=11, blank=True, null=True, verbose_name='Project Number')
    image = models.ImageField(upload_to='projects/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, 'name', Project)
        super().save(*args, **kwargs)


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=project_image_upload_to, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"{self.project.name} - Image"
