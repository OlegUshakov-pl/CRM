from .version import read_version


def app_version(request):
    return {'APP_VERSION': read_version()}
