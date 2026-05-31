from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent


def read_version():
    try:
        count = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            capture_output=True, text=True, cwd=BASE_DIR
        ).stdout.strip()
        return f'1.1.{count}'
    except Exception:
        return '1.1.0'
