from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView


urlpatterns = [
    path('', include('home.urls')),
    path('oauth/', include('oauth.urls')),
    path('admin/', admin.site.urls),
    path('flower/', RedirectView.as_view(url='/flower/'), name='flower'),
    path('discord/', RedirectView.as_view(url=settings.DISCORD_INVITE)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
