from django.shortcuts import render, redirect, get_object_or_404
from .models import Partner, Project, Task, TaskStatus, TaskAttachment, TaskComment
from .forms import PartnerForm, ProjectForm, TaskForm, TaskCommentForm
from django.contrib.auth.decorators import login_required
from core.decorators import admin_only, role_page_access
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.db import models
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.forms import modelformset_factory, inlineformset_factory
import json
from datetime import date, datetime, timedelta
from django.db.models import Q, Count, Sum
from core.models import Notification, CustomUser
from core.utils import create_notifications
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.db.models.functions import TruncMonth, TruncDate
import calendar
from django.utils import timezone
from collections import defaultdict
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Sum
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.files.base import ContentFile
import json
import os
from decimal import Decimal
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.oxml.shared import OxmlElement, qn
from docx.shared import RGBColor
import base64
from PIL import Image
import io
from docx.oxml import parse_xml

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

# Create your views here.

@login_required
def home(request):
    context = {}
    return render(request, 'clients/home.html', context)

@login_required
@role_page_access('partners')
def partner_list(request):
    if request.user.role.partner_based:
        partners = request.user.role.partners.all()
    else:
        partners = Partner.objects.all()
    return render(request, 'clients/partner_list.html', {'partners': partners})

@login_required
@role_page_access('partners')
def partner_create(request):
    if request.method == 'POST':
        form = PartnerForm(request.POST)
        if form.is_valid():
            partner = form.save()
            # Notify admins only
            admins = CustomUser.objects.filter(is_superuser=True)
            create_notifications(
                recipients=list(admins),
                message=f"A new partner '{partner.name}' has been added.",
                notif_type='info',
                actor=request.user
            )
            return redirect('partner-list')
    else:
        form = PartnerForm()
    return render(request, 'clients/partner_form.html', {'form': form})

@login_required
@role_page_access('partners')
def partner_update(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == 'POST':
        form = PartnerForm(request.POST, instance=partner)
        if form.is_valid():
            form.save()
            # Notify admins only
            admins = CustomUser.objects.filter(is_superuser=True)
            create_notifications(
                recipients=list(admins),
                message=f"Partner '{partner.name}' was updated.",
                notif_type='info',
                actor=request.user
            )
            return redirect('partner-list')
    else:
        form = PartnerForm(instance=partner)
    return render(request, 'clients/partner_form.html', {'form': form})

@login_required
@role_page_access('partners')
def partner_delete(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == 'POST':
        partner.delete()
        return redirect('partner-list')
    return render(request, 'clients/partner_confirm_delete.html', {'partner': partner})

@login_required
@role_page_access('projects')
def project_list(request):
    user = request.user

    if user.role and user.role.partner_based:
        projects = Project.objects.filter(partner__in=user.role.partners.all())
    elif user.role and user.role.name in ['Management', 'Project Manager']:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            models.Q(members=user) |
            models.Q(tasks__assignees=user)
        ).distinct()

    # Get all partners for the filter dropdown
    partners = Partner.objects.all().order_by('name')
    
    return render(request, 'clients/project_list.html', {'projects': projects, 'partners': partners})

@login_required
@role_page_access('projects')
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m()

            default_statuses = ['Pending', 'In Progress', 'Completed']
            for index, status_name in enumerate(default_statuses):
                TaskStatus.objects.create(
                    name=status_name,
                    project=project,
                    is_default=True,
                    order=index
                )
            # Notify admins and project members
            admins = CustomUser.objects.filter(is_superuser=True)
            members = project.members.all()
            recipients = set(list(admins) + list(members))
            create_notifications(
                recipients=list(recipients),
                message=f"A new project '{project.name}' has been added.",
                notif_type='info',
                actor=request.user
            )
            return redirect('project-list')
        else:
            print('FORM ERRORS:', form.errors)
            print('POST DATA:', request.POST)
    else:
        form = ProjectForm()
    return render(request, 'clients/project_form.html', {
        'form': form,
    })

@login_required
@role_page_access('projects')
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            original_members = set(project.members.all())

            project = form.save(commit=False)
            project.save()
            form.save_m2m()

            new_members = set(project.members.all())
            removed_members = original_members - new_members
            added_members = new_members - original_members
            admins = CustomUser.objects.filter(is_superuser=True)
            members = project.members.all()
            recipients = set(list(admins) + list(members))
            create_notifications(
                recipients=list(recipients),
                message=f"Project '{project.name}' was updated.",
                notif_type='info',
                actor=request.user
            )
            for user in added_members:
                create_notifications(
                    recipients=list(members),
                    message=f"{user.get_full_name() or user.username} was added to project '{project.name}'.",
                    notif_type='info',
                    actor=request.user
                )
            for user in removed_members:
                create_notifications(
                    recipients=list(members) + [user],
                    message=f"{user.get_full_name() or user.username} was removed from project '{project.name}'.",
                    notif_type='info',
                    actor=request.user
                )
            return redirect('project-list')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'clients/project_form.html', {
        'form': form,
    })

@login_required
@role_page_access('projects')
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project-list')
    return render(request, 'clients/project_confirm_delete.html', {'project': project})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    if not (user.is_staff or user.is_superuser):
        is_member = project.members.filter(pk=user.pk).exists()
        is_assigned = project.tasks.filter(models.Q(assignees=user)).exists()
        if request.user.role.name != 'Management' and not request.user.role.partner_based and request.user.role.name != 'Project Manager' and not (is_member or is_assigned):
            return redirect('project-list')
    # Calculate date 30 days ago for archiving
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Get completed status to exclude archived tasks
    completed_status = project.statuses.filter(name__iexact='completed').first()
    
    # Get all tasks except archived ones (completed 30+ days ago) for kanban view
    if completed_status:
        tasks = project.tasks.select_related('status').exclude(
            status=completed_status,
            created_at__lt=thirty_days_ago
        ).all()
    else:
        tasks = project.tasks.select_related('status').all()
    
    # Get ALL tasks (including archived) for documents modal
    all_tasks = project.tasks.select_related('status').all()
    
    statuses = project.statuses.order_by('order').all()
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            if not task.status_id:
                pending_status = statuses.filter(is_default=True, name__iexact='Pending').first()
                task.status = pending_status or statuses.first()
            task.save()
            # Save multiple assignees and add to project
            assignees = form.cleaned_data.get('assignees')
            if assignees is not None:
                task.assignees.set(assignees)
                for member in assignees:
                    if member not in project.members.all():
                        project.members.add(member)
            # Handle multiple file uploads
            for f in request.FILES.getlist('attachments'):
                TaskAttachment.objects.create(task=task, file=f)
            # Notify assigned employee and project manager
            recipients = set()
            for member in task.assignees.all():
                recipients.add(member)
            if hasattr(project, 'manager') and project.manager:
                recipients.add(project.manager)
            create_notifications(
                recipients=list(recipients),
                message=f"Task '{task.title}' was added to project '{project.name}'.",
                notif_type='info',
                actor=request.user
            )
            return redirect('project-detail', pk=project.pk)
    else:
        form = TaskForm(initial={'project': project})
        form.fields['status'].queryset = statuses
    return render(request, 'clients/project_detail.html', {'project': project, 'tasks': tasks, 'all_tasks': all_tasks, 'form': form, 'statuses': statuses})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        if 'delete_attachment' in request.POST:
            att_id = request.POST.get('delete_attachment')
            TaskAttachment.objects.filter(id=att_id, task=task).delete()
            form = TaskForm(instance=task)
            return render(request, 'clients/task_form.html', {'form': form, 'task': task, 'attachments': task.attachments.all()})
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            # Update multiple assignees
            assignees = form.cleaned_data.get('assignees')
            if assignees is not None:
                task.assignees.set(assignees)
                for member in assignees:
                    if member not in task.project.members.all():
                        task.project.members.add(member)
            # Handle multiple file uploads
            for f in request.FILES.getlist('attachments'):
                TaskAttachment.objects.create(task=task, file=f)
            # Notify assigned employee and project manager
            recipients = set()
            for member in task.assignees.all():
                recipients.add(member)
            if hasattr(task.project, 'manager') and task.project.manager:
                recipients.add(task.project.manager)
            return redirect('project-detail', pk=task.project.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'clients/task_form.html', {'form': form, 'task': task, 'attachments': task.attachments.all()})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project_pk = task.project.pk
    if request.method == 'POST':
        task.delete()
        return redirect('project-detail', pk=project_pk)
    return render(request, 'clients/task_confirm_delete.html', {'task': task})

@login_required
def task_update_status(request, pk):
    """AJAX endpoint to update a task's status via POST."""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk)
        try:
            data = json.loads(request.body)
            status_id = data.get('status_id')
            if not status_id:
                return JsonResponse({'error': 'Missing status_id'}, status=400)
            from .models import TaskStatus
            try:
                new_status = TaskStatus.objects.get(pk=status_id, project=task.project)
            except TaskStatus.DoesNotExist:
                return JsonResponse({'error': 'Invalid status_id'}, status=400)
            task.status = new_status
            task.save()
            return JsonResponse({'success': True, 'status': task.status.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@require_POST
@login_required
def add_status(request, project_id):
    from .models import TaskStatus, Project
    project = get_object_or_404(Project, pk=project_id)
    data = request.POST
    name = data.get('name')
    after_status_id = data.get('after_status_id')
    if not name:
        return JsonResponse({'error': 'Status name required'}, status=400)
    # Find the order to insert after
    statuses = list(project.statuses.order_by('order'))
    if after_status_id:
        try:
            after_status = TaskStatus.objects.get(pk=after_status_id, project=project)
            insert_order = after_status.order + 1
        except TaskStatus.DoesNotExist:
            insert_order = len(statuses)
    else:
        insert_order = len(statuses)
    # Shift orders of statuses after insert_order
    for status in statuses[::-1]:
        if status.order >= insert_order:
            status.order += 1
            status.save()
    # Create new status
    new_status = TaskStatus.objects.create(
        project=project,
        name=name,
        order=insert_order,
        is_default=False
    )
    # Return updated statuses
    updated_statuses = list(project.statuses.order_by('order').values('id', 'name', 'is_default', 'order'))
    return JsonResponse({'success': True, 'statuses': updated_statuses, 'new_status_id': new_status.id})

@require_POST
@login_required
def edit_status(request, project_id):
    from .models import TaskStatus, Project
    project = get_object_or_404(Project, pk=project_id)
    
    try:
        data = json.loads(request.body)
        status_id = data.get('status_id')
        new_name = data.get('name')
        
        if not status_id or not new_name:
            return JsonResponse({'error': 'Status ID and name are required'}, status=400)
        
        status = TaskStatus.objects.get(pk=status_id, project=project)
        
        if status.is_default:
            return JsonResponse({'error': 'Cannot edit default status'}, status=400)
        
        # Check if name already exists (excluding current status)
        if TaskStatus.objects.filter(project=project, name=new_name).exclude(pk=status_id).exists():
            return JsonResponse({'error': 'Status name already exists'}, status=400)
        
        status.name = new_name
        status.save()
        
        return JsonResponse({'success': True})
        
    except TaskStatus.DoesNotExist:
        return JsonResponse({'error': 'Status not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_POST
def reorder_statuses(request, project_id):
    from .models import Project, TaskStatus
    project = get_object_or_404(Project, pk=project_id)
    try:
        data = json.loads(request.body)
        order = data.get('order', [])
        if not isinstance(order, list):
            return JsonResponse({'error': 'Invalid order format'}, status=400)
        # Update order for each status
        for idx, status_id in enumerate(order):
            TaskStatus.objects.filter(pk=status_id, project=project).update(order=idx)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_POST
@login_required
def delete_status(request, project_id):
    from .models import Project, TaskStatus, Task
    project = get_object_or_404(Project, pk=project_id)

    try:
        data = json.loads(request.body)
        status_id = data.get('status_id')
        status = TaskStatus.objects.get(pk=status_id, project=project)
        if status.is_default:
            return JsonResponse({'error': 'Cannot delete default status'}, status=400)
        if Task.objects.filter(project=project, status=status).exists():
            return JsonResponse({'error': 'Cannot delete status with tasks'}, status=400)
        status.delete()
        return JsonResponse({'success': True})
    except TaskStatus.DoesNotExist:
        return JsonResponse({'error': 'Status not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def task_detail_panel(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    comments = task.comments.select_related('author').order_by('created_at')
    
    if request.method == 'POST':
        comment_form = TaskCommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = request.user
            
            # Handle file upload if present
            if comment_form.cleaned_data.get('attachment'):
                attachment_file = comment_form.cleaned_data['attachment']
                # Create TaskAttachment
                task_attachment = TaskAttachment.objects.create(
                    task=task,
                    file=attachment_file
                )
                comment.attachment = task_attachment
            
            comment.save()
            # Notify project members and assigned employee
            recipients = set(task.project.members.all())
            for member in task.assignees.all():
                recipients.add(member)
            for member in task.assignees.all():
                recipients.add(member)
            create_notifications(
                recipients=list(recipients),
                message=f"A new comment was added to task '{task.title}' in project '{task.project.name}'.",
                notif_type='info',
                actor=request.user
            )
            return redirect('task-detail-panel', task_id=task.id)
    else:
        comment_form = TaskCommentForm()
    
    return render(request, 'clients/task_detail_panel.html', {
        'task': task, 
        'comments': comments,
        'comment_form': comment_form
    })

@login_required
@require_POST
def add_task_comment(request, task_id):
    """AJAX endpoint to add a comment to a task."""
    task = get_object_or_404(Task, pk=task_id)
    form = TaskCommentForm(request.POST, request.FILES)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.task = task
        comment.author = request.user
        
        # Handle file upload if present
        if form.cleaned_data.get('attachment'):
            attachment_file = form.cleaned_data['attachment']
            # Create TaskAttachment
            task_attachment = TaskAttachment.objects.create(
                task=task,
                file=attachment_file
            )
            comment.attachment = task_attachment
        
        comment.save()
        
        # Generate attachment HTML if present
        attachment_html = ""
        if comment.attachment:
            attachment = comment.attachment
            fname = attachment.file.name.lower()
            shortname = attachment.file.name[-20:] if len(attachment.file.name) > 20 else attachment.file.name
            
            if fname.endswith(('.jpg', '.jpeg', '.png')):
                attachment_html = f"""
                <div class="mt-2">
                    <small class="text-muted">📎 Attached:</small>
                    <a href="{attachment.file.url}" target="_blank" class="d-block mt-1" title="{attachment.file.name}">
                        <img src="{attachment.file.url}" alt="Image" class="img-thumbnail" style="max-width:80px; max-height:80px; object-fit:cover;">
                    </a>
                </div>
                """
            elif fname.endswith('.pdf'):
                attachment_html = f"""
                <div class="mt-2">
                    <small class="text-muted">📎 Attached:</small>
                    <a href="{attachment.file.url}" target="_blank" class="d-flex align-items-center mt-1 text-decoration-none">
                        <i class="fa fa-file-pdf text-danger me-2"></i>
                        <span>{shortname}</span>
                    </a>
                </div>
                """
            elif fname.endswith(('.doc', '.docx')):
                attachment_html = f"""
                <div class="mt-2">
                    <small class="text-muted">📎 Attached:</small>
                    <a href="{attachment.file.url}" target="_blank" class="d-flex align-items-center mt-1 text-decoration-none">
                        <i class="fa fa-file-word text-primary me-2"></i>
                        <span>{shortname}</span>
                    </a>
                </div>
                """
            elif fname.endswith(('.xls', '.xlsx')):
                attachment_html = f"""
                <div class="mt-2">
                    <small class="text-muted">📎 Attached:</small>
                    <a href="{attachment.file.url}" target="_blank" class="d-flex align-items-center mt-1 text-decoration-none">
                        <i class="fa fa-file-excel text-success me-2"></i>
                        <span>{shortname}</span>
                    </a>
                </div>
                """
            else:
                attachment_html = f"""
                <div class="mt-2">
                    <small class="text-muted">📎 Attached:</small>
                    <a href="{attachment.file.url}" target="_blank" class="d-flex align-items-center mt-1 text-decoration-none">
                        <i class="fa fa-file text-secondary me-2"></i>
                        <span>{shortname}</span>
                    </a>
                </div>
                """
        
        # Return the new comment HTML for AJAX response
        comment_html = f"""
        <div class="comment-item border-bottom pb-3 mb-3">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div class="d-flex align-items-center">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2" style="width: 32px; height: 32px;">
                        <small class="fw-bold">{comment.author.first_name[0] if comment.author.first_name else comment.author.username[0]}</small>
                    </div>
                    <div>
                        <strong class="d-block">{comment.author.get_full_name() or comment.author.username}</strong>
                        <small class="text-muted">{comment.created_at.strftime('%b %d, %Y %H:%M')}</small>
                    </div>
                </div>
            </div>
            <div class="comment-content ps-4">
                <span class="processed-content">{comment.content.replace(chr(10), '<br>')}</span>
                {attachment_html}
            </div>
        </div>
        """
        
        return JsonResponse({
            'success': True,
            'comment_html': comment_html,
            'comment_count': task.comments.count()
        })
    else:
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

@login_required
def archived_tasks(request, project_id):
    """Get archived tasks (completed 30+ days ago) for a project"""
    project = get_object_or_404(Project, pk=project_id)
    
    # Check if user has access to this project
    user = request.user
    if not (user.is_staff or user.is_superuser):
        is_member = project.members.filter(pk=user.pk).exists()
        is_assigned = project.tasks.filter(models.Q(assignees=user)).exists()
        if request.user.role.name != 'Management' and not request.user.role.partner_based and request.user.role.name != 'Project Manager' and not (is_member or is_assigned):
            return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Calculate date 30 days ago
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Get completed tasks that are 30+ days old
    completed_status = project.statuses.filter(name__iexact='completed').first()
    if not completed_status:
        return JsonResponse({'tasks': []})
    
    archived_tasks = Task.objects.filter(
        project=project,
        status=completed_status,
        created_at__lt=thirty_days_ago
    ).order_by('-created_at')
    
    # Format tasks for JSON response
    tasks_data = []
    for task in archived_tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'assigned_to_id': task.assignees.first().id if task.assignees.exists() else None,
            'assigned_to_name': task.assignees.first().get_full_name() if task.assignees.exists() else 'Unassigned',
            'completed_at': task.created_at.isoformat(),
            'description': task.description or '',
            'priority': task.priority,
            'created_at': task.created_at.isoformat()
        })
    
    return JsonResponse({'tasks': tasks_data})



@login_required
def archived_tasks(request, project_id):
    """Get archived tasks (completed 30+ days ago) for a project"""
    project = get_object_or_404(Project, pk=project_id)
    
    # Check if user has access to this project
    user = request.user
    if not (user.is_staff or user.is_superuser):
        is_member = project.members.filter(pk=user.pk).exists()
        is_assigned = project.tasks.filter(assignees=user).exists()
        if request.user.role.name != 'Management' and not request.user.role.partner_based and request.user.role.name != 'Project Manager' and not (is_member or is_assigned):
            return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Calculate date 30 days ago
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Get completed tasks that are 30+ days old
    completed_status = project.statuses.filter(name__iexact='completed').first()
    if not completed_status:
        return JsonResponse({'tasks': []})
    
    archived_tasks = Task.objects.filter(
        project=project,
        status=completed_status,
        created_at__lt=thirty_days_ago
    ).order_by('-created_at')
    
    # Format tasks for JSON response
    tasks_data = []
    for task in archived_tasks:
        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'assigned_to_id': task.assignees.first().id if task.assignees.exists() else None,
            'assigned_to_name': task.assignees.first().get_full_name() if task.assignees.exists() else 'Unassigned',
            'completed_at': task.created_at.isoformat(),
            'description': task.description or '',
            'priority': task.priority,
            'created_at': task.created_at.isoformat()
        })
    
    return JsonResponse({'tasks': tasks_data})