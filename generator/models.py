from django.db import models
from django.contrib.auth.models import User
from core.models import TimeStampedModel, generate_unique_slug
from companies.models import Company
from contacts.models import Contact


class Deal(TimeStampedModel):
    """
    EXAMPLE MODEL — Deal (Sales Pipeline)
    Rename or replace this model with your own.
    This demonstrates all common field types used across the CRM.
    """

    STATUS_CHOICES = [
        ('lead', 'Lead'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lead')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name='Deal Value')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    contacts = models.ManyToManyField(Contact, blank=True, related_name='deals')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_deals')
    due_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Deal'
        verbose_name_plural = 'Deals'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, 'name', Deal)
        super().save(*args, **kwargs)