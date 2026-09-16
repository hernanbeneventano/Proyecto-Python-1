from datetime import date  # para comparar fechas con la fecha actual
from rest_framework import serializers  # para crear serializadores de DRF
from .models import Project, Task, Tag  # traemos los modelos que vamos a convertir a JSON


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag  # modelo que representa la etiqueta
        fields = ["id", "name"]  # qué campos devolver en la respuesta JSON


# Este serializador representa una tarea. Acá definimos cómo se ve la tarea cuando la API la responde
# y también validamos que no se creen datos inconsistentes.
class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)  # cada tarea puede tener varias etiquetas

    class Meta:
        model = Task  # modelo de tarea
        fields = [
            "id", "project", "title", "description",
            "priority", "status", "due_date", "tags", "created_at",
        ]  # campos que se van a serializar

    # Validamos la fecha para que no se pueda poner una fecha pasada
    def validate_due_date(self, value):
        if value and value < date.today():  # si la fecha es anterior a hoy, no sirve
            raise serializers.ValidationError("La fecha límite no puede ser en el pasado.")  # error de validación
        return value  # si está bien, devuelve la fecha

    # Acá se chequean reglas que dependen de varios campos juntos, como estado + fecha + proyecto
    def validate(self, data):
        status = data.get("status", getattr(self.instance, "status", None))  # toma el estado nuevo o el actual
        project = data.get("project", getattr(self.instance, "project", None))  # toma el proyecto nuevo o el actual

        # Si la tarea está completada, tiene que tener fecha de vencimiento
        if status == "completada" and not data.get("due_date") and not getattr(self.instance, "due_date", None):
            raise serializers.ValidationError(
                "No se puede marcar una tarea como completada sin fecha límite registrada."
            )  # una tarea completada necesita fecha

        # Una tarea no puede empezar si el proyecto todavía no tiene ninguna completada
        if status == "en_progreso" and project is not None:
            completed_tasks = Task.objects.filter(project=project, status="completada")  # busca tareas completadas del mismo proyecto
            if self.instance is not None:
                completed_tasks = completed_tasks.exclude(pk=self.instance.pk)  # excluye la tarea actual si se está editando

            if not completed_tasks.exists():
                raise serializers.ValidationError(
                    "No se puede poner una tarea en progreso si el proyecto no tiene ninguna tarea completada todavía."
                )  # regla de negocio: no se puede empezar una tarea si aún no hay ninguna completada

        return data  # si todo está bien, devuelve los datos validados


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)  # incluye las tareas relacionadas dentro del proyecto

    class Meta:
        model = Project  # modelo de proyecto
        fields = ["id", "name", "description", "tasks", "created_at"]  # campos serializados del proyecto

