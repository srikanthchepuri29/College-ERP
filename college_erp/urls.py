from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import home_page

urlpatterns = [
    # Django Admin relocated to prevent collision
    path('django-admin/', admin.site.urls),
    
    # Home Page
    path('', home_page, name='home'),
    
    # Authentication (Login / Register) URLs mapped at root
    path('', include('accounts.urls')),
    
    # Dashboard URLs
    path('dashboard/', include('dashboard.urls')),
    
    # REST API Configuration
    path('api/', include('api.urls')),
]

# Serve media and static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
