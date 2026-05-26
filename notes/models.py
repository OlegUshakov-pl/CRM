from django.db import models
from core.models import TimeStampedModel
from contacts.models import Contact, Company
from projects.models import Project


class Note(TimeStampedModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='note_entries')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='note_entries')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='note_entries')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
