from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('candidates.urls')),
    path('hiring/', include('employers.urls')),
    path('', include('pwa.urls')),
]
#    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)