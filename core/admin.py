from django.contrib import admin
from .models import Project, ProjectMembership, SecurityLog, Task, Tag
 
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Tag)
admin.site.register(ProjectMembership)
admin.site.register(SecurityLog)
