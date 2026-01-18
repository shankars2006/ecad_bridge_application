# ecadbridge/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views  # import your new views

handler404 = 'ecadbridge.views.custom_page_not_found_view'

urlpatterns = [
    path('hakuna_matata/', admin.site.urls),
    path('', include('blog.urls')),
    path('accounts/', include('allauth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
