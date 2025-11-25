from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Partner)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(TaskStatus)
admin.site.register(TaskAttachment)
admin.site.register(TaskComment)