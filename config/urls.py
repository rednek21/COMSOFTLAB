from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from emails.api.routers import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('emails.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
