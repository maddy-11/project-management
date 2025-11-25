from .models import CompanyProfile
from core.models import Notification
 
def company_profile(request):
    profile = CompanyProfile.objects.first()
    return {'company_profile': profile}

# Add this context processor for sidebar permissions

def user_page_access(request):
    if request.user.is_staff or request.user.is_superuser:
        return {'user_page_access': ["user-list", "dashboard", "company-profile", "department-list""role-list", "partners", "projects", "salary",]}
    elif request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role:
        print(request.user.role.page_access)
        return {'user_page_access': request.user.role.page_access or []}
    return {'user_page_access': []} 

def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    else:
        count = 0
    return {'notification_count': count}

def user_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:10]
    else:
        notifications = []
    return {'user_notifications': notifications} 