from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls',namespace="accounts")),
    path('accounts/', include('django.contrib.auth.urls')),
    path('',views.HomePage.as_view(), name="home"),
    path('',include('Cyberabad.urls',namespace="Cyberabad")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)