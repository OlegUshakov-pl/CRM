import os
import sys
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / '.env'


def _load_env_file(path=None):
    """Load KEY=VALUE pairs from a local .env file.

    Real environment variables always win over values from the file.
    """
    path = path or ENV_FILE
    try:
        raw = path.read_text(encoding='utf-8')
    except OSError:
        return
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and value:
            os.environ.setdefault(key, value)


def _env_bool(name, default='False'):
    return os.environ.get(name, default).lower() in ('true', '1', 'yes')


_load_env_file()

DEBUG = _env_bool('DEBUG')


def _secret_key():
    """Env key -> .env key -> generate and persist a random local key."""
    if os.environ.get('DJANGO_SECRET_KEY'):
        return os.environ['DJANGO_SECRET_KEY']
    key = get_random_secret_key()
    try:
        current = ENV_FILE.read_text(encoding='utf-8') if ENV_FILE.exists() else ''
        if current and not current.endswith('\n'):
            current += '\n'
        ENV_FILE.write_text(current + f'DJANGO_SECRET_KEY={key}\n', encoding='utf-8')
    except OSError:
        if not DEBUG:
            raise ImproperlyConfigured(
                'DJANGO_SECRET_KEY is not set and it could not be written to .env. '
                'Set DJANGO_SECRET_KEY in the environment before running with DEBUG=False.'
            )
        sys.stderr.write('[config] Could not write .env, using an in-memory SECRET_KEY.\n')
    else:
        sys.stderr.write(f'[config] Generated a new SECRET_KEY in {ENV_FILE}\n')
    return key


SECRET_KEY = _secret_key()

_hosts_raw = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _hosts_raw.split(',') if h.strip()] if _hosts_raw else ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'accounts',
    'companies',
    'contacts',
    'projects',
    'materials',
    'tasks',
    'notes',
    'generator',
    'documents',
    'parts',
    'assistant',
    'calendar_app',
    'library',
    'library_articles',
    'library_gallery',
    'library_files',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.app_version',
                'core.context_processors.sidebar_projects',
                'core.context_processors.current_workspace',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DOCUMENTS_ROOT = BASE_DIR / 'documents'
DOCUMENTS_URL = '/files/'

PROJECT_ROOT_PATH = str(BASE_DIR / 'media')

LIBRARY_ROOT = BASE_DIR / 'media' / 'library'

AI_FILES_ROOT = BASE_DIR / 'ai_files'
AI_FILES_URL = '/ai-files/'
AI_FILES_MAX_SIZE = 50 * 1024 * 1024
AI_FILES_TOTAL_QUOTA = 1024 * 1024 * 1024

AI_BROWSER_BLACKLIST = [
    'malware-site.example',
    'phishing.example',
]
AI_BROWSER_TIMEOUT = 20

OLLAMA_BASE_URL = 'http://localhost:11434'
OLLAMA_DEFAULT_MODEL = ''

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Password reset — console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Session security
# SECURE_COOKIES must be enabled behind HTTPS; keep it off for plain-HTTP LAN access.
SECURE_COOKIES = _env_bool('SECURE_COOKIES', str(not DEBUG))
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

X_FRAME_OPTIONS = 'SAMEORIGIN'

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
