# pizza_app/urls.py (principal)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('carta_digital.urls')),
]

# Esto agrega las rutas para archivos estáticos (CSS, JS, imágenes) y media
# Solo se activa si settings.DEBUG es True (modo desarrollo).
# En producción (settings.DEBUG = False), estas rutas no se añaden.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# En producción (DEBUG=False), WhiteNoise manejará los archivos estáticos.
# Para los archivos media en producción, Render (o tu servidor web)
# necesitará configuración adicional (ej. Persistent Disk o un servicio de almacenamiento en la nube).
