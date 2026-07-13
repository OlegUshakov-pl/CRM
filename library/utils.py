import os
import re
import shutil
import urllib.request
from django.conf import settings
from django.core.files.storage import default_storage
from core.models import AppSetting, AppSettings


def get_library_root():
    root = AppSettings.get_value('storage.project_path', '')
    if root:
        path = os.path.join(root, 'library')
    elif AppSetting.get_value('project_root_path', ''):
        root = AppSetting.get_value('project_root_path', '')
        AppSettings.set_value('storage.project_path', root)
        path = os.path.join(root, 'library')
    elif hasattr(settings, 'PROJECT_ROOT_PATH') and settings.PROJECT_ROOT_PATH:
        path = os.path.join(settings.PROJECT_ROOT_PATH, 'library')
    else:
        path = os.path.join(str(settings.MEDIA_ROOT), 'library')
    os.makedirs(path, exist_ok=True)
    return path


def sanitize_folder_name(name):
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'[\s]+', '_', name)
    name = name.strip().rstrip('. ')
    return name or 'untitled'


def get_article_folder_name(item):
    slug = sanitize_folder_name(item.slug or item.title)
    date_str = item.created_at.strftime('%Y-%m-%d')
    return f'{slug}_{date_str}'


def get_article_folder_path(item):
    root = get_library_root()
    folder_name = get_article_folder_name(item)
    return os.path.join(root, folder_name)


def create_article_folder(item):
    folder_path = get_article_folder_path(item)
    os.makedirs(folder_path, exist_ok=True)
    images_path = os.path.join(folder_path, 'images')
    os.makedirs(images_path, exist_ok=True)
    return folder_path


def save_article_as_md(item, content, images=None):
    folder_path = create_article_folder(item)
    md_filename = get_article_folder_name(item) + '.md'
    md_path = os.path.join(folder_path, md_filename)
    images_dir = os.path.join(folder_path, 'images')
    os.makedirs(images_dir, exist_ok=True)

    if images:
        for img_name, img_data in images.items():
            img_path = os.path.join(images_dir, img_name)
            mode = 'wb' if isinstance(img_data, bytes) else 'w'
            with open(img_path, mode) as f:
                f.write(img_data)

    img_pattern = re.compile(r'<img\s+[^>]*src="([^"]+)"', re.IGNORECASE)
    found_srcs = img_pattern.findall(content)
    media_root = str(settings.MEDIA_ROOT)

    for src in found_srcs:
        try:
            if src.startswith('/media/'):
                rel_path = src[len('/media/'):]
                local_path = os.path.normpath(os.path.join(media_root, rel_path))
                if os.path.exists(local_path):
                    img_name = os.path.basename(src)
                    dest = os.path.join(images_dir, img_name)
                    if not os.path.exists(dest):
                        shutil.copy2(local_path, dest)
                    content = content.replace(src, f'/library/{item.slug}/image/{img_name}')
            elif src.startswith('http'):
                img_name = src.split('/')[-1].split('?')[0]
                if not img_name or '.' not in img_name:
                    img_name = f'img_{len(os.listdir(images_dir))+1}.jpg'
                dest = os.path.join(images_dir, img_name)
                if not os.path.exists(dest):
                    urllib.request.urlretrieve(src, dest)
                content = content.replace(src, f'/library/{item.slug}/image/{img_name}')
        except Exception:
            pass

    if item.file:
        try:
            src_path = item.file.path
            if os.path.exists(src_path):
                img_name = os.path.basename(src_path)
                dest = os.path.join(images_dir, img_name)
                if not os.path.exists(dest):
                    shutil.copy2(src_path, dest)
        except Exception:
            pass

    if item.preview_image:
        try:
            src_path = item.preview_image.path
            if os.path.exists(src_path):
                img_name = os.path.basename(src_path)
                dest = os.path.join(images_dir, img_name)
                if not os.path.exists(dest):
                    shutil.copy2(src_path, dest)
        except Exception:
            pass

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return md_path, content


def delete_item_from_disk(item):
    try:
        if item.file and os.path.exists(item.file.path):
            item.file.delete(save=False)
    except Exception:
        pass
    try:
        if item.preview_image and os.path.exists(item.preview_image.path):
            item.preview_image.delete(save=False)
    except Exception:
        pass
    try:
        for att in item.attachments.all():
            if att.file and os.path.exists(att.file.path):
                att.file.delete(save=False)
    except Exception:
        pass
    if item.content or (item.source_url and not item.file):
        folder_path = get_article_folder_path(item)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path, ignore_errors=True)
            except Exception:
                pass
