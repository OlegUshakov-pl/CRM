from .version import read_version


def app_version(request):
    return {'APP_VERSION': read_version()}


def sidebar_projects(request):
    from projects.models import Project
    projects = Project.objects.filter(is_active=True).select_related('company').order_by('name')[:50]
    return {'sidebar_projects': projects}
