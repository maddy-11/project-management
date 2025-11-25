from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='clients-home'),
    # Partner management
    path('partners/', views.partner_list, name='partner-list'),
    path('partners/create/', views.partner_create, name='partner-create'),
    path('partners/<int:pk>/edit/', views.partner_update, name='partner-update'),
    path('partners/<int:pk>/delete/', views.partner_delete, name='partner-delete'),
    # Project management
    path('projects/', views.project_list, name='project-list'),
    path('projects/create/', views.project_create, name='project-create'),
    path('projects/<int:pk>/edit/', views.project_update, name='project-update'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project-delete'),
    path('projects/<int:pk>/', views.project_detail, name='project-detail'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task-update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task-delete'),
    path('task/<int:pk>/update_status/', views.task_update_status, name='task-update-status'),
    # Task comments
    path('tasks/<int:task_id>/panel/', views.task_detail_panel, name='task-detail-panel'),
    path('tasks/<int:task_id>/add_comment/', views.add_task_comment, name='add-task-comment'),
    # Data summary
    path('projects/<int:project_id>/add_status/', views.add_status, name='add-status'),
    path('projects/<int:project_id>/edit_status/', views.edit_status, name='edit-status'),
    path('projects/<int:project_id>/reorder_statuses/', views.reorder_statuses, name='reorder-statuses'),
    path('projects/<int:project_id>/delete_status/', views.delete_status, name='delete-status'),
    path('projects/<int:project_id>/archived_tasks/', views.archived_tasks, name='archived-tasks'),

]