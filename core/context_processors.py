from .version import read_version


def app_version(request):
    return {'APP_VERSION': read_version()}


def sidebar_projects(request):
    from projects.models import Project
    projects = Project.objects.filter(is_active=True).select_related('company').order_by('name')[:50]
    return {'sidebar_projects': projects}


def current_workspace(request):
    path = request.path
    if path.startswith('/library/') or path.startswith('/workspace/collections'):
        ws = 'collections'
    elif path.startswith('/projects/') or path.startswith('/workspace/projects'):
        ws = 'projects'
    elif path.startswith('/materials/') or path.startswith('/parts/') or path.startswith('/documents/') or path.startswith('/tasks/') or path.startswith('/contacts/') or path.startswith('/companies/') or path.startswith('/notes/'):
        ws = 'projects'
    else:
        ws = 'none'
    return {'current_workspace': ws}
