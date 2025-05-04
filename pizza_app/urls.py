from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('carta_digital.urls')),  # <-- Cambia a solo 'carta_digital.urls'
]

# 👇 Esto agrega las rutas para archivos estáticos (CSS, JS, imágenes)
if settings.DEBUG == False:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)