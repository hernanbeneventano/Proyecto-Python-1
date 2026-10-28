import logging

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotFound,
    PermissionDenied,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Project, ProjectMembership, SecurityLog
from .permissions import IsProjectAdminOrReadOnly
from .repositories import TaskRepository
from .serializers import ProjectSerializer, TaskSerializer
from .serializers_auth import AuditedTokenObtainPairSerializer, RegisterSerializer
from .services import MembershipService, TaskService
from .throttles import LoginRateThrottle

security_logger = logging.getLogger("security")


def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})


def _request_ip(request):
    return request.META.get("REMOTE_ADDR")


def _safe_log_username(value):
    if not isinstance(value, str):
        return ""
    return "".join(character for character in value[:150] if character.isprintable())


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("id")
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectAdminOrReadOnly]

    def get_queryset(self):
        return MembershipService.projects_for(self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            project = serializer.save()
            ProjectMembership.objects.create(
                project=project, user=self.request.user, role="admin"
            )

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        project = self.get_object()
        username = request.data.get("username")
        role = request.data.get("role", "miembro")

        if not isinstance(username, str) or not username.strip():
            return Response(
                {"detail": "Se requiere un nombre de usuario."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(role, str) or role not in dict(ProjectMembership.ROLE_CHOICES):
            return Response(
                {"detail": "El rol debe ser 'admin' o 'miembro'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(get_user_model(), username=username.strip())
        membership, created = ProjectMembership.objects.get_or_create(
            project=project, user=user, defaults={"role": role}
        )
        if not created:
            return Response(
                {"detail": "El usuario ya es miembro de este proyecto."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        SecurityLog.objects.create(
            user=request.user,
            action="member_added",
            detail=f"user_id={user.pk} role={membership.role}",
            ip_address=_request_ip(request),
        )
        return Response(
            {
                "id": membership.pk,
                "project": project.pk,
                "user": user.pk,
                "username": user.get_username(),
                "role": membership.role,
            },
            status=status.HTTP_201_CREATED,
        )


class TaskViewSet(viewsets.ModelViewSet):
    queryset = TaskRepository.get_queryset()
    serializer_class = TaskSerializer
    filterset_fields = ["status", "priority", "project"]
    ordering_fields = ["due_date", "created_at", "priority"]
    search_fields = ["title", "description"]
    permission_classes = [IsAuthenticated, IsProjectAdminOrReadOnly]

    def get_queryset(self):
        return super().get_queryset().filter(
            project__memberships__user=self.request.user
        ).distinct()

    def check_project_admin(self, project, action):
        if not MembershipService.is_member(self.request.user, project):
            raise NotFound()
        if not MembershipService.is_admin(self.request.user, project):
            SecurityLog.objects.create(
                user=self.request.user,
                action="permission_denied",
                detail=action,
                ip_address=_request_ip(self.request),
            )
            raise PermissionDenied(
                "Solo un admin del proyecto puede crear o mover tareas en él."
            )

    def perform_create(self, serializer):
        self.check_project_admin(
            serializer.validated_data["project"],
            "task_create",
        )
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        if "project" in serializer.validated_data:
            self.check_project_admin(
                serializer.validated_data["project"],
                "task_project_change",
            )
        serializer.save()

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        TaskService.mark_completed(task)
        return Response(self.get_serializer(task).data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        tasks = TaskService.tasks_overdue(self.get_queryset())
        page = self.paginate_queryset(tasks)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(tasks, many=True).data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class SocialLoginJWTView(APIView):
    """
    Emite JWT para el usuario que allauth autenticó mediante su sesión Django.
    """

    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        return Response(
            {"refresh": str(refresh), "access": str(refresh.access_token)}
        )


class ThrottledTokenObtainPairView(TokenObtainPairView):
    serializer_class = AuditedTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except AuthenticationFailed:
            username = _safe_log_username(request.data.get("username", ""))
            ip_address = _request_ip(request)
            SecurityLog.objects.create(
                action="login_failed",
                detail=f"usuario={username}"[:255],
                ip_address=ip_address,
            )
            security_logger.warning(
                "Login fallido para usuario %s desde %s",
                username,
                ip_address,
            )
            raise