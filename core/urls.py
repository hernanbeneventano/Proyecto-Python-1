from django.urls import path, include

from core.views import health_check

import core.views as views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"projects", views.ProjectViewSet, basename="project")
router.register(r"tasks", views.TaskViewSet, basename="task")


urlpatterns = [
    path('', health_check, name='health_check'),
    path("projects/", views.project_list, name="project_list"),
    path("tasks/", views.task_list, name="task_list"),
    path("api/", include(router.urls)),
]