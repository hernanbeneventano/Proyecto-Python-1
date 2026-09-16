from django.http import JsonResponse  # para devolver respuestas JSON simples
from rest_framework.decorators import api_view  # para convertir funciones en endpoints de API
from rest_framework.response import Response  # responde con JSON ya serializado por DRF
from rest_framework import viewsets  # para crear CRUD con ModelViewSet
from .models import Project, Task  # modelos del proyecto
from .serializers import ProjectSerializer, TaskSerializer  # serializadores que convierten modelos a JSON


# Este endpoint sirve para saber si la API está levantada y funcionando
# En la práctica es una prueba rápida para comprobar que el servidor responde
# y que la app está bien conectada.
def health_check(request):
    return JsonResponse({"status": "ok", "service": "TaskFlow API"})  # devuelve un JSON simple con el estado del servicio


# Esta vista lista todos los proyectos que hay en la base de datos.
# Como es un GET, solo trae datos y los devuelve serializados en JSON.
@api_view(["GET"])
def project_list(request):
    projects = Project.objects.all()  # traigo todos los proyectos de la base
    serializer = ProjectSerializer(projects, many=True)  # convierto los proyectos a JSON
    return Response(serializer.data)  # devuelvo la lista en respuesta HTTP


# Esta vista trae todas las tareas y además precarga la relación con el proyecto y con sus tags.
# Así evitamos problemas de consultas repetidas y la respuesta llega más completa.
@api_view(["GET"])
def task_list(request):
    tasks = Task.objects.select_related("project").prefetch_related("tags").all()  # traigo tareas con el proyecto y etiquetas relacionadas
    serializer = TaskSerializer(tasks, many=True)  # convierto las tareas a JSON
    return Response(serializer.data)  # devuelvo la respuesta con la lista


# Con ModelViewSet ya no hace falta escribir el CRUD manualmente.
# Django se encarga de crear las operaciones básicas para proyectos.
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()  # todos los proyectos disponibles
    serializer_class = ProjectSerializer  # serializador para proyectos


# Lo mismo pasa con tareas, pero con relaciones cargadas para evitar errores de rendimiento.
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related("project").prefetch_related("tags").all()  # tareas con relaciones cargadas
    serializer_class = TaskSerializer  # serializador para tareas