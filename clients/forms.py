from django import forms
from .models import Partner, Project, Task, TaskStatus, TaskAttachment, TaskComment
from django.contrib.auth import get_user_model
import json

class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['name', 'email', 'phone', 'address', 'type', 'info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Project
        fields = ['name', 'description', 'partner', 'members', 'project_type', 'link']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,  # reduces height
                'style': 'resize: vertical;',  # optional: controls resizing
            }),
            'link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=commit)
        return instance

class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select assignees-select'})
    )
    class Meta:
        model = Task
        fields = ['title', 'project', 'assignees', 'created_by', 'status', 'priority', 'description']
        widgets = {
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'project' in self.initial:
            project = self.initial['project']
            self.fields['status'].queryset = TaskStatus.objects.filter(project=project).order_by('order')
            # Prefer suggesting project members first for assignees
            self.fields['assignees'].queryset = get_user_model().objects.all()

class TaskStatusForm(forms.ModelForm):
    class Meta:
        model = TaskStatus
        fields = ['name', 'order']

class TaskCommentForm(forms.ModelForm):
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.jpg,.jpeg,.png,.pdf,.doc,.docx,.xls,.xlsx,.txt,.zip,.rar'
        })
    )
    
    class Meta:
        model = TaskComment
        fields = ['content']  # Remove 'attachment' since it's handled separately
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment... @mention someone'
            })
        } 
