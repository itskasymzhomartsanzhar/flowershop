from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
import os

#DATACHANGE
admin.site.site_header = 'Панель Swift Store V2.0'

urlpatterns = [
    path('secretadmin/', admin.site.urls),
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)