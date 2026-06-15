from django.core.management.base import BaseCommand
from core.models import AIProvider, AppSetting, AppSettings


PROVIDERS = [
    {'id': 'anthropic', 'name': 'Anthropic', 'type': 'cloud'},
    {'id': 'openai', 'name': 'OpenAI', 'type': 'cloud'},
    {'id': 'google', 'name': 'Google AI', 'type': 'cloud'},
    {'id': 'mistral', 'name': 'Mistral', 'type': 'cloud'},
    {'id': 'groq', 'name': 'Groq', 'type': 'cloud'},
    {'id': 'deepseek', 'name': 'DeepSeek', 'type': 'cloud'},
    {'id': 'openrouter', 'name': 'OpenRouter', 'type': 'aggregator'},
    {'id': 'opencode', 'name': 'OpenCode', 'type': 'cloud'},
    {'id': 'ollama', 'name': 'Ollama', 'type': 'local'},
]


class Command(BaseCommand):
    help = 'Seed AI providers and migrate existing AppSetting data to AppSettings'

    def handle(self, *args, **options):
        for p in PROVIDERS:
            obj, created = AIProvider.objects.get_or_create(
                id=p['id'],
                defaults={'name': p['name'], 'type': p['type']}
            )
            if created:
                self.stdout.write(f'  Created provider: {p["name"]}')
            else:
                self.stdout.write(f'  Provider exists: {p["name"]}')

        old_keys = ['project_root_path', 'subfolder_documents', 'subfolder_drawings', 'subfolder_models']
        new_keys = ['storage.project_path', 'storage.subfolders']

        for old_key, new_key in zip(old_keys, new_keys):
            val = AppSetting.get_value(old_key, '')
            if val:
                AppSettings.set_value(new_key, val)
                self.stdout.write(f'  Migrated {old_key} -> {new_key}')

        self.stdout.write(self.style.SUCCESS('Done!'))
