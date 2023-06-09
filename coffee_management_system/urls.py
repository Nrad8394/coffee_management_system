from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from coffee_management_system import settings


urlpatterns = [
    path('admin1/', admin.site.urls),
    path('', include('coffee_management_app.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
