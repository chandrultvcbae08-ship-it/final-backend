from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    return JsonResponse({
        'service': 'MediConnect Healthcare API',
        'status': 'healthy',
        'version': '1.0.0',
        'endpoints': {
            'accounts': '/api/accounts/',
            'doctors': '/api/doctors/',
            'appointments': '/api/appointments/',
            'prescriptions': '/api/prescriptions/',
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/doctors/', include('doctors.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/prescriptions/', include('prescriptions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
