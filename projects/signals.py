import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Project
from core.models import AppSetting


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

    safe_number = sanitize_folder_name(instance.number)
    safe_name = sanitize_folder_name(instance.name)
    base_folder_name = f"{safe_number}_{safe_name}_Project"
    folder_path = get_unique_folder_path(root_path, base_folder_name)

    os.makedirs(folder_path, exist_ok=True)
