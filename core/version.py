from pathlib import Path
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent


def read_version():
    return '1.2.001'
