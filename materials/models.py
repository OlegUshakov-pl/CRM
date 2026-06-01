from django.db import models
from core.models import TimeStampedModel, generate_unique_slug
from projects.models import Project


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Material(TimeStampedModel):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('m', 'Meters'),
        ('m2', 'Square Meters'),
        ('m3', 'Cubic Meters'),
        ('l', 'Liters'),
        ('set', 'Sets'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='materials', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='materials')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, 'name', Material)
        super().save(*args, **kwargs)

    def total_price(self):
        if self.unit_price and self.quantity:
            return self.quantity * self.unit_price
