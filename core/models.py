from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Activity(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} {self.action} {self.description}"


def log_activity(user, action, description, obj=None):
    kwargs = {
        'user': user,
        'action': action,
        'description': description,
    }
    if obj:
        kwargs['content_type'] = ContentType.objects.get_for_model(obj)
        kwargs['object_id'] = obj.pk
    Activity.objects.create(**kwargs)


def generate_unique_slug(instance, source_field, ModelClass):
    base_slug = slugify(getattr(instance, source_field))
    if not base_slug:
        base_slug = 'untitled'
    slug = base_slug
    counter = 1
    while ModelClass.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
