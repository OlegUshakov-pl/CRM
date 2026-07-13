from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from slugify import slugify
import os
import base64


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Activity(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    description = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    object_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

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


class AppSetting(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Application Setting'
        verbose_name_plural = 'Application Settings'

    def __str__(self):
        return self.key

    @classmethod
    def get_value(cls, key, default=''):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_value(cls, key, value):
        obj, _ = cls.objects.update_or_create(key=key, defaults={'value': value})
        return obj


def generate_unique_slug(instance, source_field, ModelClass):
    base_slug = slugify(getattr(instance, source_field))
    if not base_slug:
        base_slug = 'untitled'

    from django.db import IntegrityError

    slug = base_slug
    counter = 1
    max_attempts = 100

    for _ in range(max_attempts):
        with transaction.atomic():
            if not ModelClass._base_manager.select_for_update().filter(slug=slug).exclude(pk=instance.pk).exists():
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

    import uuid
    return f"{base_slug}-{uuid.uuid4().hex[:8]}"


def _get_encryption_key():
    key_hex = os.environ.get('ENCRYPTION_KEY', '')
    if not key_hex:
        return None
    try:
        return bytes.fromhex(key_hex)
    except ValueError:
        return None


def encrypt_api_key(plaintext):
    key = _get_encryption_key()
    if not key or not plaintext:
        return plaintext
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        import secrets
        iv = secrets.token_bytes(12)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)
        return f"{iv.hex()}:{ciphertext[:16].hex()}:{ciphertext[16:].hex()}"
    except ImportError:
        return plaintext


def decrypt_api_key(encrypted):
    key = _get_encryption_key()
    if not key or not encrypted:
        return encrypted
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        parts = encrypted.split(':')
        if len(parts) != 3:
            return encrypted
        iv = bytes.fromhex(parts[0])
        ciphertext = bytes.fromhex(parts[1]) + bytes.fromhex(parts[2])
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(iv, ciphertext, None).decode('utf-8')
    except (ImportError, Exception):
        return encrypted


def mask_api_key(key):
    if not key or len(key) <= 8:
        return '***'
    return key[:6] + '•' * (len(key) - 10) + key[-4:]


class AIProvider(models.Model):
    TYPE_CHOICES = [
        ('cloud', 'Cloud'),
        ('local', 'Local'),
        ('aggregator', 'Aggregator'),
    ]

    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    api_key_enc = models.TextField(blank=True, null=True, db_column='api_key_enc')
    base_url = models.CharField(max_length=500, blank=True, null=True)
    selected_model = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    key_verified_at = models.DateTimeField(blank=True, null=True)
    models_synced_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'AI Provider'
        verbose_name_plural = 'AI Providers'

    def __str__(self):
        return self.name

    def set_api_key(self, key):
        self.api_key_enc = encrypt_api_key(key) if key else None

    def get_api_key(self):
        if not self.api_key_enc:
            return ''
        return decrypt_api_key(self.api_key_enc)

    def get_masked_key(self):
        return mask_api_key(self.get_api_key())

    def save(self, *args, **kwargs):
        if self.is_active:
            AIProvider.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class AIModel(models.Model):
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='models')
    model_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    is_custom = models.BooleanField(default=False)
    tags = models.JSONField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'AI Model'
        verbose_name_plural = 'AI Models'
        unique_together = ('provider', 'model_id')
        indexes = [
            models.Index(fields=['provider']),
        ]

    def __str__(self):
        return f"{self.provider.name}: {self.name}"


class AppSettings(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    value = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'App Setting'
        verbose_name_plural = 'App Settings'

    def __str__(self):
        return self.key

    @classmethod
    def get_value(cls, key, default=''):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_value(cls, key, value):
        obj, _ = cls.objects.update_or_create(key=key, defaults={'value': value})
        return obj

    @classmethod
    def get_all(cls):
        return {s.key: s.value for s in cls.objects.all()}
