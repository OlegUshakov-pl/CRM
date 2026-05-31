from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parent.parent / 'VERSION'


def read_version():
    try:
        return VERSION_FILE.read_text().strip()
    except FileNotFoundError:
        return '0.0.0'


def bump_version():
    parts = read_version().split('.')
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    patch += 1
    new_version = f'{major}.{minor}.{patch}'
    VERSION_FILE.write_text(new_version + '\n')
    return new_version
