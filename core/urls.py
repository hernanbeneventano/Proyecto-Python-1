from django.contrib import admin
from django.urls import path, include

from core import views
from core.views import health_check

urlpatterns = [
path("admin/", admin.site.urls),
path("health/", views.health_check, name="health_check"),
]