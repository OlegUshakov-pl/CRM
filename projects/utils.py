import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from core.models import AppSetting


def sanitize_folder_name(name):
    invalid_chars = '<>:"/\\|?*'
    for c in invalid_chars:
        name = name.replace(c, '_')
    return name.strip().rstrip('. ')


def get_subfolder_name(project_number, setting_key, default_suffix):
    from core.models import AppSetting
    safe_number = sanitize_folder_name(project_number) if project_number else ''
    template = AppSetting.get_value(setting_key, '')
    if template:
        return template.replace('{Number}', safe_number)
    return f'{safe_number}_{default_suffix}'


def get_project_folder_path(project):
    root_path = AppSetting.get_value('project_root_path', '')
    if not root_path:
        return None
    safe_number = sanitize_folder_name(project.number or '')
    safe_name = sanitize_folder_name(project.name)
    folder_name = f"{safe_number}_{safe_name}_Project"
    return os.path.join(root_path, folder_name)


def ensure_project_subfolder(project, subfolder_name):
    project_path = get_project_folder_path(project)
    if not project_path or not os.path.exists(project_path):
        return None
    subpath = os.path.join(project_path, subfolder_name)
    os.makedirs(subpath, exist_ok=True)
    return subpath


def get_project_subfolder_path(project, subfolder_name):
    project_path = get_project_folder_path(project)
    if not project_path:
        return None
    return os.path.join(project_path, subfolder_name)


class ProjectFileSystemStorage(FileSystemStorage):
    def __init__(self, fallback=None):
        self._fallback = fallback
        super().__init__(location=settings.MEDIA_ROOT)

    def _get_location(self):
        root = AppSetting.get_value('project_root_path', '')
        if root:
            os.makedirs(root, exist_ok=True)
            return root
        return self._fallback or super().location

    def path(self, name):
        return os.path.join(self._get_location(), name)

    def _save(self, name, content):
        full_path = self.path(name)
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(full_path, 'wb+') as f:
            for chunk in content.chunks():
                f.write(chunk)
        return name

    def _open(self, name, mode='rb'):
        return super(FileSystemStorage, self)._open(name, mode)

    def exists(self, name):
        return os.path.exists(self.path(name))

    def delete(self, name):
        if self.exists(name):
            os.remove(self.path(name))

    def size(self, name):
        return os.path.getsize(self.path(name))

    def url(self, name):
        from django.urls import reverse
        return reverse('core:serve_project_file', kwargs={'file_path': name})
