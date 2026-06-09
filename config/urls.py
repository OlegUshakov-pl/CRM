from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('companies/', include('companies.urls')),
    path('contacts/', include('contacts.urls')),
    path('projects/', include('projects.urls')),
    path('tasks/', include('tasks.urls')),
    path('notes/', include('notes.urls')),
    path('materials/', include('materials.urls')),
    path('deals/', include('generator.urls')),
    path('documents/', include('documents.urls')),
    path('parts/', include('parts.urls')),
    path('assistant/', include('assistant.urls')),
    path('calendar/', include('calendar_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.DOCUMENTS_URL, document_root=settings.DOCUMENTS_ROOT)
    urlpatterns += static(settings.AI_FILES_URL, document_root=settings.AI_FILES_ROOT)
