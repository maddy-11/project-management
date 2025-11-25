from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='company-profile'),
    path('profile/edit/', views.profile_edit, name='company-profile-edit'),
    path('departments/', views.department_list, name='department-list'),
    path('departments/create/', views.department_create, name='department-create'),
    path('departments/<int:pk>/edit/', views.department_update, name='department-update'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department-delete'),
    path('bank-accounts/', views.bank_account_list, name='bank-account-list'),
    path('bank-accounts/create/', views.bank_account_create, name='bank-account-create'),
    path('bank-accounts/<int:pk>/edit/', views.bank_account_update, name='bank-account-update'),
    path('bank-accounts/<int:pk>/delete/', views.bank_account_delete, name='bank-account-delete'),
    path('roles/', views.role_list, name='role-list'),
    path('roles/create/', views.role_create, name='role-create'),
    path('roles/<int:pk>/edit/', views.role_update, name='role-update'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role-delete'),
    # User profile URLs
    path('user/profile/', views.user_profile, name='user-profile'),
    path('user/profile/edit/', views.user_profile_edit, name='user-profile-edit'),
    path('user/change-password/', views.change_password, name='change-password'),
    path('notifications/', views.notifications_list, name='notifications-list'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='notifications-mark-all-read'),
    path('notifications/clear-all/', views.clear_all_notifications, name='notifications-clear-all'),
    # User Management URLs
    path('users/', views.user_list, name='user-list'),
    path('users/create/', views.user_create, name='user-create'),
    path('users/<int:pk>/', views.user_detail, name='user-detail'),
    path('users/<int:pk>/edit/', views.user_update, name='user-update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user-delete'),
    path('users/<int:pk>/change-password/', views.user_change_password, name='user-change-password'),
] 