import os
from django.db import models
from django.core.validators import MinValueValidator
from core.models import TimeStampedModel, generate_unique_slug
from projects.models import Project


def material_file_upload_to(instance, filename):
    material = instance.material
    if material and material.project and material.project.number:
        from documents.models import get_project_folder_name
        from projects.utils import sanitize_folder_name
        project_folder = get_project_folder_name(material.project)
        safe_number = sanitize_folder_name(material.number) if material.number else 'no_number'
        materials_subfolder = f'{safe_number}_materials'
        return os.path.join(project_folder, materials_subfolder, filename)
    return os.path.join('_no_project', 'materials', filename)


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

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='materials', blank=True, null=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name='materials', db_index=True)
    number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Material Number', db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
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
        if self.unit_price is not None and self.quantity is not None:
            return self.quantity * self.unit_price
        return 0


class MaterialFile(models.Model):
    from projects.utils import ProjectFileSystemStorage

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='files', db_index=True)
    file = models.FileField(upload_to=material_file_upload_to, storage=ProjectFileSystemStorage())
    original_name = models.CharField(max_length=255, blank=True)
    size = models.IntegerField(blank=True, null=True, help_text='File size in bytes')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.original_name or os.path.basename(self.file.name) if self.file else ''

    def save(self, *args, **kwargs):
        if not self.original_name and self.file:
            self.original_name = os.path.basename(self.file.name)
        if self.file and not self.size:
            try:
                self.size = self.file.size
            except Exception:
                pass
        super().save(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else ''
