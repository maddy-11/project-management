# core/decorators.py
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import redirect

def admin_only(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.role and u.role.name == 'Management',
        login_url='/accounts/login'
    )(view_func)

# Decorator to restrict access based on role's allowed pages
def role_page_access(page_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('/accounts/login')
            if user.is_staff or user.is_superuser or (user.role and page_name in (user.role.page_access or [])):
                return view_func(request, *args, **kwargs)
            return redirect('/accounts/login')
        return _wrapped_view
    return decorator
