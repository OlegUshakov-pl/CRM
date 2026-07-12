import os
import re
import shutil
from django.conf import settings


def get_library_root():
    return str(settings.LIBRARY_ROOT)


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
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    if images:
        images_dir = os.path.join(folder_path, 'images')
        os.makedirs(images_dir, exist_ok=True)
        for img_name, img_data in images.items():
            img_path = os.path.join(images_dir, img_name)
            mode = 'wb' if isinstance(img_data, bytes) else 'w'
            with open(img_path, mode) as f:
                f.write(img_data)
    return md_path


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
