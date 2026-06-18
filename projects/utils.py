import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from core.models import AppSetting, AppSettings


def get_project_root_path():
    root = AppSettings.get_value('storage.project_path', '')
    if root:
        return root
    root = AppSetting.get_value('project_root_path', '')
    if root:
        AppSettings.set_value('storage.project_path', root)
        return root
    if hasattr(settings, 'PROJECT_ROOT_PATH') and settings.PROJECT_ROOT_PATH:
        return settings.PROJECT_ROOT_PATH
    return ''


def sanitize_folder_name(name):
    invalid_chars = '<>:"/\\|?*'
    for c in invalid_chars:
        name = name.replace(c, '_')
    return name.strip().rstrip('. ')


def get_subfolder_name(project_number, setting_key, default_suffix):
    from core.models import AppSetting, AppSettings
    safe_number = sanitize_folder_name(project_number) if project_number else ''
    template = AppSettings.get_value(setting_key, '')
    if not template:
        template = AppSetting.get_value(setting_key, '')
    if template:
        return template.replace('{Number}', safe_number)
    return f'{safe_number}_{default_suffix}'


def get_project_folder_path(project):
    root_path = get_project_root_path()
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


def cleanup_empty_dirs(folder_path):
    if not folder_path or not os.path.exists(folder_path):
        return
    while folder_path and os.path.exists(folder_path) and folder_path != get_project_root_path():
        if not os.listdir(folder_path):
            os.rmdir(folder_path)
            folder_path = os.path.dirname(folder_path)
        else:
            break


def rename_project_folder(project, old_number, old_name):
    from django.db.models import Q
    old_safe_number = sanitize_folder_name(old_number) if old_number else ''
    old_safe_name = sanitize_folder_name(old_name)
    old_folder_name = f"{old_safe_number}_{old_safe_name}_Project"
    root_path = get_project_root_path()
    if not root_path:
        return
    old_path = os.path.join(root_path, old_folder_name)
    if not os.path.exists(old_path):
        return
    new_safe_number = sanitize_folder_name(project.number) if project.number else ''
    new_safe_name = sanitize_folder_name(project.name)
    new_folder_name = f"{new_safe_number}_{new_safe_name}_Project"
    new_path = os.path.join(root_path, new_folder_name)
    if old_path == new_path:
        return
    old_subs = {}
    if os.path.exists(old_path):
        for entry in os.listdir(old_path):
            entry_path = os.path.join(old_path, entry)
            if os.path.isdir(entry_path):
                old_subs[entry] = entry_path
    new_subs = {}
    for old_sub_name, old_sub_path in old_subs.items():
        new_sub_name = old_sub_name
        if old_safe_number and old_sub_name.startswith(f'{old_safe_number}_'):
            suffix = old_sub_name[len(f'{old_safe_number}_'):]
            new_sub_name = f'{new_safe_number}_{suffix}'
        new_sub_path = os.path.join(old_path, new_sub_name)
        new_subs[old_sub_name] = new_sub_path
    file_updates = []
    for model_class, file_field_name, project_rel in _get_file_models():
        filter_q = Q(**{f'{file_field_name}__contains': old_folder_name})
        queryset = model_class.objects.filter(**{f'{project_rel}': project}).filter(filter_q)
        for obj in queryset:
            old_file = getattr(obj, file_field_name)
            if old_file and old_file.name and old_folder_name in old_file.name:
                new_name = old_file.name.replace(old_folder_name, new_folder_name, 1)
                for old_sub, new_sub_path in new_subs.items():
                    if old_sub in new_name:
                        new_sub_name_actual = os.path.basename(new_sub_path)
                        new_name = new_name.replace(old_sub, new_sub_name_actual, 1)
                file_updates.append((obj, file_field_name, old_file, new_name))
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
    for old_sub_name, new_sub_path in new_subs.items():
        new_sub_actual = os.path.basename(new_sub_path)
        old_sub_full = os.path.join(new_path, old_sub_name)
        new_sub_full = os.path.join(new_path, new_sub_actual)
        if os.path.exists(old_sub_full) and old_sub_full != new_sub_full:
            os.rename(old_sub_full, new_sub_full)
    for obj, file_field_name, old_file, new_name in file_updates:
        old_file.name = new_name
        setattr(obj, file_field_name, old_file)
        obj.save(update_fields=[file_field_name])
    if project.image and project.image.name and old_folder_name in project.image.name:
        new_img_name = project.image.name.replace(old_folder_name, new_folder_name, 1)
        for old_sub, new_sub_path in new_subs.items():
            if old_sub in new_img_name:
                new_img_name = new_img_name.replace(old_sub, os.path.basename(new_sub_path), 1)
        project.image.name = new_img_name
        project.save(update_fields=['image'])


def _get_file_models():
    from documents.models import Document
    from parts.models import Part
    from materials.models import MaterialFile
    from .models import ProjectImage
    return [
        (Document, 'file', 'project'),
        (Part, 'file', 'project'),
        (MaterialFile, 'file', 'material__project'),
        (ProjectImage, 'image', 'project'),
    ]


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
        root = get_project_root_path()
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
        return super()._open(name, mode)

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
