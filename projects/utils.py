import os
from core.models import AppSetting


def sanitize_folder_name(name):
    invalid_chars = '<>:"/\\|?*'
    for c in invalid_chars:
        name = name.replace(c, '_')
    return name.strip().rstrip('. ')


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
