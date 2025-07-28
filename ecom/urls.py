from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
]

<<<<<<< HEAD
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======
]

if settings.DEBUG:
    # Static files should still be served in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
>>>>>>> e94d237 (✅ Setup Cloudinary storage and update requirements)
