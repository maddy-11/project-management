from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

# Create your models here.

class Partner(models.Model):
    LOCAL = 'local'
    OVERSEAS = 'overseas'
    PARTNER_TYPE_CHOICES = [
        (LOCAL, 'Local'),
        (OVERSEAS, 'Overseas'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.TextField()
    type = models.CharField(max_length=10, choices=PARTNER_TYPE_CHOICES)
    info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    PROJECT_TYPE_LOCAL = 'local'
    PROJECT_TYPE_OVERSEAS = 'overseas'
    PROJECT_TYPE_CHOICES = [
        (PROJECT_TYPE_LOCAL, 'Local'),
        (PROJECT_TYPE_OVERSEAS, 'Overseas'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    members = models.ManyToManyField(get_user_model(), related_name='projects', blank=True)
    project_type = models.CharField(max_length=10, choices=PROJECT_TYPE_CHOICES, default=PROJECT_TYPE_LOCAL)
    link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

class TaskStatus(models.Model):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='statuses')
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField()
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ('project', 'name')
        ordering = ['order']

    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITY_LOW = 'Low'
    PRIORITY_MEDIUM = 'Medium'
    PRIORITY_HIGH = 'High'
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]
    title = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    assigned_to = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    assignees = models.ManyToManyField(get_user_model(), blank=True, related_name='assigned_tasks_multi')
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default=PRIORITY_LOW)
    status = models.ForeignKey(TaskStatus, on_delete=models.PROTECT, related_name='tasks')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='task_comments')
    content = models.TextField()
    attachment = models.ForeignKey(TaskAttachment, on_delete=models.SET_NULL, null=True, blank=True, related_name='comment')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"