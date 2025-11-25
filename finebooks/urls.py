from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import profile_view, profile_edit, user_profile, user_profile_edit, change_password

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clients.urls')),
    path('profile/', profile_view, name='company-profile'),
    path('profile/edit/', profile_edit, name='company-profile-edit'),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # User profile URLs (accessible to all authenticated users)
    path('user/profile/', user_profile, name='user-profile'),
    path('user/profile/edit/', user_profile_edit, name='user-profile-edit'),
    path('user/change-password/', change_password, name='change-password'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
