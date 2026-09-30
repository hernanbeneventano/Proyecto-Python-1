from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Project, Tag, Task


class Command(BaseCommand):
    help = "Carga datos de prueba con proyectos, etiquetas y tareas para probar la API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Borra primero los datos existentes antes de cargar los demo data",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Borrando datos existentes..."))
            Task.objects.all().delete()
            Project.objects.all().delete()
            Tag.objects.all().delete()

        projects_data = [
            {
                "name": "Proyecto Alpha",
                "description": "Gestión de tareas internas y planificación semanal.",
                "tasks": [
                    ("Diseñar flujo de onboarding", "alta", "completada", 3),
                    ("Revisar backlog del sprint", "media", "en_progreso", 2),
                    ("Preparar reunión de requisitos", "baja", "pendiente", 5),
                    ("Actualizar documentación de clientes", "media", "pendiente", 8),
                    ("Validar mocks de UI", "alta", "completada", 10),
                ],
            },
            {
                "name": "Proyecto Beta",
                "description": "Mantenimiento y mejora del sistema de ventas.",
                "tasks": [
                    ("Corregir errores de cobro", "alta", "completada", 1),
                    ("Analizar tasa de conversión", "media", "en_progreso", 4),
                    ("Exportar reportes CSV", "baja", "pendiente", 7),
                    ("Auditar permisos de usuarios", "alta", "pendiente", 12),
                    ("Preparar release de producción", "alta", "completada", 15),
                ],
            },
            {
                "name": "Proyecto Gamma",
                "description": "Evolución de la plataforma de soporte y atención.",
                "tasks": [
                    ("Mapear incidentes críticos", "alta", "completada", 2),
                    ("Crear dashboard de SLA", "media", "en_progreso", 6),
                    ("Revisar tiempos de respuesta", "media", "pendiente", 9),
                    ("Documentar casos recurrentes", "baja", "pendiente", 11),
                    ("Capacitar equipo de soporte", "media", "completada", 14),
                ],
            },
            {
                "name": "Proyecto Delta",
                "description": "Modernización del proceso de facturación digital.",
                "tasks": [
                    ("Revisar facturas pendientes", "alta", "completada", 0),
                    ("Implementar validación de IVA", "alta", "en_progreso", 3),
                    ("Mejorar mensajes de error", "media", "pendiente", 5),
                    ("Subir scan de comprobantes", "baja", "pendiente", 10),
                    ("Probar integración con clientes", "alta", "completada", 18),
                ],
            },
            {
                "name": "Proyecto Epsilon",
                "description": "Desarrollo del módulo de inventario automatizado.",
                "tasks": [
                    ("Diseñar esquema de stock", "alta", "completada", 2),
                    ("Definir reglas de reorden", "media", "en_progreso", 4),
                    ("Validar procesos de baja", "alta", "pendiente", 6),
                    ("Actualizar catalogo online", "media", "pendiente", 9),
                    ("Generar informe de movimiento", "baja", "completada", 20),
                ],
            },
        ]

        all_tags = [
            "backend",
            "frontend",
            "qa",
            "infra",
            "bugfix",
            "documentacion",
            "cliente",
            "soporte",
            "ventas",
            "proceso",
        ]

        tag_map = {}
        for tag_name in all_tags:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tag_map[tag_name] = tag

        created_projects = 0
        created_tasks = 0

        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                name=project_data["name"],
                defaults={"description": project_data["description"]},
            )
            if created:
                created_projects += 1

            selected_tags = list(tag_map.values())
            task_index = 0

            for title, priority, status, days_offset in project_data["tasks"]:
                task_index += 1
                due_date = (timezone.now().date() + timedelta(days=days_offset))

                task = Task.objects.create(
                    project=project,
                    title=title,
                    description=(
                        f"Tarea de prueba para {project.name}. "
                        f"Estado: {status}. Prioridad: {priority}."
                    ),
                    priority=priority,
                    status=status,
                    due_date=due_date,
                )

                task.tags.set(
                    [
                        selected_tags[(task_index + len(project.name)) % len(selected_tags)],
                        selected_tags[(task_index * 2 + 1) % len(selected_tags)],
                    ]
                )
                created_tasks += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Datos demo cargados correctamente: {created_projects} proyectos y {created_tasks} tareas."
            )
        )
