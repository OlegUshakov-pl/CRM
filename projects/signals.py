import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Project
from core.models import AppSetting
from .utils import get_subfolder_name


def sanitize_folder_name(name):
    invalid_chars = '<>:"/\\|?*'
    for c in invalid_chars:
        name = name.replace(c, '_')
    return name.strip().rstrip('. ')


def get_unique_folder_path(root_path, base_name):
    path = os.path.join(root_path, base_name)
    if not os.path.exists(path):
        return path
    now = timezone.now().strftime('%d.%m.%Y')
    counter = 1
    while True:
        suffix = f"_(Copy from {now})"
        if counter > 1:
            suffix = f"_(Copy from {now})_{counter}"
        new_name = f"{base_name}{suffix}"
        path = os.path.join(root_path, new_name)
        if not os.path.exists(path):
            return path
        counter += 1
        if counter > 1000:
            return os.path.join(root_path, f"{base_name}_(Copy from {now})_{counter}")


@receiver(post_save, sender=Project)
def create_project_folders(sender, instance, created, raw, **kwargs):
    if not created or raw:
        return
    if not instance.number:
        return

    root_path = AppSetting.get_value('project_root_path', '')
    if not root_path:
        return

    documents_folder_name = get_subfolder_name(instance.number, 'subfolder_documents', 'documents')
    drawings_folder_name = get_subfolder_name(instance.number, 'subfolder_drawings', 'drawings')
    models_folder_name = get_subfolder_name(instance.number, 'subfolder_models', 'models')

    os.makedirs(os.path.join(root_path, documents_folder_name), exist_ok=True)
    os.makedirs(os.path.join(root_path, drawings_folder_name), exist_ok=True)
    os.makedirs(os.path.join(root_path, models_folder_name), exist_ok=True)
