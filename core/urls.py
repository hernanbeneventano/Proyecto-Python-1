from django.urls import path

from core.views import health_check

import core.views as views


urlpatterns = [
    path('', health_check, name='health_check'),
    path("projects/", views.project_list, name="project_list"),
    path("tasks/", views.task_list, name="task_list"),
]