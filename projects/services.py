import json
import logging
import shutil
import tempfile
import zipfile
from pathlib import Path

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

EXPORT_VERSION = 1


class ExportService:
    def __init__(self, project):
        self.project = project
        self.tmp_dir = None
        self.export_dir = None

    def export(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix='crm_export_'))
        self.export_dir = self.tmp_dir / 'export'
        self.export_dir.mkdir()

        try:
            self._build_json()
            zip_path = self._create_zip()
            return zip_path
        except Exception:
            self.cleanup()
            raise

    def _build_json(self):
        p = self.project
        project_data = {
            'number': p.number or '',
            'name': p.name,
            'description': p.description or '',
            'status': p.status,
            'start_date': p.start_date.isoformat() if p.start_date else None,
            'end_date': p.end_date.isoformat() if p.end_date else None,
            'budget': str(p.budget) if p.budget else None,
            'created_at': timezone.localtime(p.created_at).isoformat() if p.created_at else None,
            'created_by_username': p.created_by.username if p.created_by else None,
            'image_name': p.image.name if p.image else None,
        }
        if p.image and p.image.name:
            self._copy_file_to_export(p.image.path, p.image.name)

        data = {
            'export_version': EXPORT_VERSION,
            'project': project_data,
            'materials': self._serialize_materials(),
            'tasks': self._serialize_tasks(),
            'notes': self._serialize_notes(),
            'documents': self._serialize_documents(),
            'parts': self._serialize_parts(),
            'images': self._serialize_images(),
        }
        (self.export_dir / 'export.json').write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8'
        )

    def _serialize_materials(self):
        result = []
        for m in self.project.materials.select_related('category').all():
            result.append({
                'name': m.name,
                'category': m.category.name if m.category else None,
                'quantity': str(m.quantity),
                'unit': m.unit,
                'unit_price': str(m.unit_price) if m.unit_price else None,
                'notes': m.notes or '',
            })
        return result

    def _serialize_tasks(self):
        result = []
        for t in self.project.tasks.all():
            result.append({
                'title': t.title,
                'description': t.description or '',
                'status': t.status,
                'priority': t.priority,
                'due_date': t.due_date.isoformat() if t.due_date else None,
            })
        return result

    def _serialize_notes(self):
        result = []
        for n in self.project.note_entries.all():
            result.append({
                'title': n.title,
                'content': n.content,
                'date': n.date.isoformat() if n.date else None,
            })
        return result

    def _serialize_documents(self):
        result = []
        for d in self.project.documents.all():
            entry = {
                'number': d.number or '',
                'file_type': d.file_type,
                'size': d.size,
                'file_name': d.file.name if d.file else None,
            }
            if d.file and d.file.name:
                self._copy_file_to_export(d.file.path, d.file.name)
            result.append(entry)
        return result

    def _serialize_parts(self):
        result = []
        for p in self.project.parts.select_related('category').all():
            entry = {
                'number': p.number or '',
                'category': p.category.name if p.category else None,
                'size': p.size or '',
                'rev': p.rev or '',
                'created': p.created.isoformat() if p.created else None,
                'updated': p.updated.isoformat() if p.updated else None,
                'file_name': p.file.name if p.file else None,
            }
            if p.file and p.file.name:
                self._copy_file_to_export(p.file.path, p.file.name)
            result.append(entry)
        return result

    def _serialize_images(self):
        result = []
        for img in self.project.images.all():
            entry = {
                'image_name': img.image.name if img.image else None,
            }
            if img.image and img.image.name:
                self._copy_file_to_export(img.image.path, img.image.name)
            result.append(entry)
        return result

    def _copy_file_to_export(self, src_path, file_name):
        try:
            src = Path(src_path)
            if not src.exists():
                logger.warning('File not found during export: %s', src_path)
                return
            dst = self.export_dir / 'files' / file_name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dst))
        except Exception as e:
            logger.error('Failed to copy file %s: %s', src_path, e)

    def _create_zip(self):
        zip_path = self.tmp_dir / f'{self.project.name}.zip'
        with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in self.export_dir.walk():
                for file in files:
                    file_path = root / file
                    arcname = file_path.relative_to(self.export_dir)
                    zf.write(str(file_path), str(arcname))
        return zip_path

    def cleanup(self):
        if self.tmp_dir and self.tmp_dir.exists():
            shutil.rmtree(str(self.tmp_dir), ignore_errors=True)


class ImportService:
    def __init__(self, zip_file):
        self.zip_file = zip_file
        self.tmp_dir = None
        self.export_dir = None
        self.errors = []

    def validate(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix='crm_import_'))
        try:
            with zipfile.ZipFile(self.zip_file, 'r') as zf:
                bad = zf.testzip()
                if bad:
                    self.errors.append(f'Corrupted file in archive: {bad}')
                    return False
                zf.extractall(str(self.tmp_dir))
        except zipfile.BadZipFile:
            self.errors.append('Invalid ZIP file.')
            return False
        except Exception as e:
            self.errors.append(f'Failed to extract archive: {e}')
            return False

        json_path = self.tmp_dir / 'export.json'
        if not json_path.exists():
            self.errors.append('export.json not found in archive.')
            return False

        try:
            self.export_data = json.loads(json_path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as e:
            self.errors.append(f'Invalid JSON in export.json: {e}')
            return False

        version = self.export_data.get('export_version')
        if version != EXPORT_VERSION:
            self.errors.append(
                f'Unsupported export version {version}. Expected {EXPORT_VERSION}.'
            )
            return False

        files_dir = self.tmp_dir / 'files'
        if not files_dir.exists():
            self.errors.append('files/ directory not found in archive.')
            return False

        self._check_files(files_dir)
        return len(self.errors) == 0

    def _check_files(self, files_dir):
        image_name = self.export_data.get('project', {}).get('image_name')
        if image_name:
            file_path = files_dir / image_name
            if not file_path.exists():
                self.errors.append(f'Missing file: {image_name}')

        sections = ['documents', 'parts', 'images']
        for section in sections:
            for entry in self.export_data.get(section, []):
                file_name = entry.get('file_name') or entry.get('image_name')
                if file_name:
                    file_path = files_dir / file_name
                    if not file_path.exists():
                        self.errors.append(f'Missing file: {file_name}')

    def import_project(self):
        from .models import Project, ProjectImage
        from documents.models import Document
        from materials.models import Material, Category as MaterialCategory
        from tasks.models import Task
        from notes.models import Note
        from parts.models import Part, Category as PartCategory

        project_data = self.export_data['project']
        project = Project.objects.create(
            number=project_data.get('number') or None,
            name=project_data['name'],
            description=project_data.get('description') or '',
            status=project_data.get('status', 'planning'),
            start_date=project_data.get('start_date'),
            end_date=project_data.get('end_date'),
            budget=project_data.get('budget'),
            created_at=project_data.get('created_at'),
        )

        files_dir = self.tmp_dir / 'files'

        image_name = project_data.get('image_name')
        if image_name:
            src = files_dir / image_name
            if src.exists():
                project.image.save(image_name, open(str(src), 'rb'), save=True)

        for m_data in self.export_data.get('materials', []):
            category = None
            if m_data.get('category'):
                category, _ = MaterialCategory.objects.get_or_create(
                    name=m_data['category']
                )
            Material.objects.create(
                project=project,
                category=category,
                name=m_data['name'],
                quantity=m_data.get('quantity', '1'),
                unit=m_data.get('unit', 'pcs'),
                unit_price=m_data.get('unit_price'),
                notes=m_data.get('notes', ''),
            )

        for t_data in self.export_data.get('tasks', []):
            Task.objects.create(
                project=project,
                title=t_data['title'],
                description=t_data.get('description', ''),
                status=t_data.get('status', 'todo'),
                priority=t_data.get('priority', 'medium'),
                due_date=t_data.get('due_date'),
            )

        for n_data in self.export_data.get('notes', []):
            Note.objects.create(
                project=project,
                title=n_data['title'],
                content=n_data['content'],
                date=n_data.get('date'),
            )

        for d_data in self.export_data.get('documents', []):
            file_name = d_data.get('file_name')
            doc = Document(
                project=project,
                number=d_data.get('number') or None,
                file_type=d_data.get('file_type', 'other'),
                size=d_data.get('size'),
            )
            if file_name:
                src = files_dir / file_name
                if src.exists():
                    doc.file.save(file_name, open(str(src), 'rb'), save=True)
                else:
                    doc.save()
            else:
                doc.save()

        for p_data in self.export_data.get('parts', []):
            category = None
            if p_data.get('category'):
                category, _ = PartCategory.objects.get_or_create(
                    name=p_data['category']
                )
            part = Part(
                project=project,
                category=category,
                number=p_data.get('number', ''),
                size=p_data.get('size', ''),
                rev=p_data.get('rev', ''),
                created=p_data.get('created'),
                updated=p_data.get('updated'),
            )
            file_name = p_data.get('file_name')
            if file_name:
                src = files_dir / file_name
                if src.exists():
                    part.file.save(file_name, open(str(src), 'rb'), save=True)
                else:
                    part.save()
            else:
                part.save()

        for i_data in self.export_data.get('images', []):
            file_name = i_data.get('image_name')
            if file_name:
                src = files_dir / file_name
                if src.exists():
                    img = ProjectImage(project=project)
                    img.image.save(file_name, open(str(src), 'rb'), save=True)

        return project

    def cleanup(self):
        if self.tmp_dir and self.tmp_dir.exists():
            shutil.rmtree(str(self.tmp_dir), ignore_errors=True)
