from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
admin.site.register(CompanyProfile)
admin.site.register(Department)
admin.site.register(Role)
admin.site.register(Notification)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom admin configuration for CustomUser"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('is_superuser', 'is_active', 'role', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    
    def get_queryset(self, request):
        """Filter out superusers except admin"""
        from django.db.models import Q
        qs = super().get_queryset(request)
        # return qs.filter(Q(is_superuser=False) | Q(username='admin'))
        return qs
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Role & Access', {'fields': ('role',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'is_active'),
        }),
    )
