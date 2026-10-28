from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Project, ProjectMembership, SecurityLog, Task
from .serializers import TaskSerializer


class SecurityFeatureTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_description_is_sanitized(self):
        serializer = TaskSerializer()

        self.assertEqual(
            serializer.validate_description(
                "<script>alert(1)</script>Hola <b>mundo</b>"
            ),
            "Hola mundo",
        )

    @patch("core.views.security_logger.warning")
    def test_login_failures_are_logged_and_throttled(self, _warning):
        for attempt in range(5):
            response = self.client.post(
                "/api/token/",
                {"username": "admin", "password": f"incorrecta-{attempt}"},
                format="json",
            )
            self.assertEqual(response.status_code, 401)

        throttled_response = self.client.post(
            "/api/token/",
            {"username": "admin", "password": "incorrecta"},
            format="json",
        )

        self.assertEqual(throttled_response.status_code, 429)
        self.assertIn("Retry-After", throttled_response)
        self.assertEqual(SecurityLog.objects.filter(action="login_failed").count(), 5)
        self.assertEqual(
            SecurityLog.objects.filter(action="login_failed").first().detail,
            "usuario=admin",
        )

    def test_successful_login_is_logged(self):
        user = get_user_model().objects.create_user(
            username="usuario",
            password="Contrasena-segura-123",
        )

        response = self.client.post(
            "/api/token/",
            {"username": user.username, "password": "Contrasena-segura-123"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            SecurityLog.objects.filter(
                user=user,
                action="login_success",
                ip_address="127.0.0.1",
            ).exists()
        )

    def test_cors_allows_configured_origin_only(self):
        allowed = self.client.get(
            "/",
            HTTP_ORIGIN="http://localhost:3000",
        )
        disallowed = self.client.get(
            "/",
            HTTP_ORIGIN="http://sitio-malicioso.com",
        )

        self.assertEqual(
            allowed["access-control-allow-origin"],
            "http://localhost:3000",
        )
        self.assertNotIn("access-control-allow-origin", disallowed)

    def test_member_denied_task_update_is_audited(self):
        user = get_user_model().objects.create_user(
            username="miembro",
            password="Contrasena-segura-123",
        )
        project = Project.objects.create(name="Proyecto")
        ProjectMembership.objects.create(
            project=project,
            user=user,
            role="miembro",
        )
        task = Task.objects.create(project=project, title="Tarea original")
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            f"/api/tasks/{task.pk}/",
            {"title": "Tarea modificada"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            SecurityLog.objects.filter(
                user=user,
                action="permission_denied",
                detail="PATCH task",
                ip_address="127.0.0.1",
            ).exists()
        )

    def test_non_member_cannot_discover_task(self):
        user = get_user_model().objects.create_user(
            username="externo",
            password="Contrasena-segura-123",
        )
        project = Project.objects.create(name="Proyecto privado")
        task = Task.objects.create(project=project, title="Tarea privada")
        self.client.force_authenticate(user=user)

        response = self.client.get(f"/api/tasks/{task.pk}/")

        self.assertEqual(response.status_code, 404)
