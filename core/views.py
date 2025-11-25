from django.shortcuts import render, redirect, get_object_or_404
from .models import CompanyProfile, Department, Role, Notification, CustomUser, BankAccount
from .forms import DepartmentForm, RoleForm, BankAccountForm, CustomUserCreationForm, CustomUserUpdateForm, CustomUserPasswordForm
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .utils import create_notifications
from django.db.models import Q
# Create your views here.

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['name', 'email', 'phone', 'bio', 'logo']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            valid_extensions = ['jpeg', 'jpg', 'png', 'svg']
            ext = logo.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Only JPEG, JPG, PNG, and SVG files are allowed for the logo.')
        return logo

@login_required
def profile_view(request):
    profile, created = CompanyProfile.objects.get_or_create(pk=1)
    bank_accounts = BankAccount.objects.filter(is_active=True).order_by('bank_name', 'account_holder_name')
    return render(request, 'core/profile.html', {
        'profile': profile,
        'bank_accounts': bank_accounts
    })

@login_required
def profile_edit(request):
    profile, created = CompanyProfile.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Notify everyone
            users = CustomUser.objects.all()
            create_notifications(
                recipients=list(users),
                message="The company profile was updated.",
                notif_type='info',
                actor=request.user
            )
            return redirect('company-profile')
    else:
        form = CompanyProfileForm(instance=profile)
    return render(request, 'core/profile_edit.html', {'form': form, 'profile': profile})

# Department views
@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'core/department_list.html', {'departments': departments})

@login_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            # Notify everyone
            users = CustomUser.objects.all()
            create_notifications(
                recipients=list(users),
                message=f"A new department '{department.name}' has been added.",
                notif_type='info',
                actor=request.user
            )
            return redirect('department-list')
    else:
        form = DepartmentForm()
    return render(request, 'core/department_form.html', {'form': form, 'title': 'Add Department'})

@login_required
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            # Notify everyone
            users = CustomUser.objects.all()
            create_notifications(
                recipients=list(users),
                message=f"Department '{department.name}' was updated.",
                notif_type='info',
                actor=request.user
            )
            return redirect('department-list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'core/department_form.html', {'form': form, 'department': department, 'title': 'Edit Department'})

@login_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        return redirect('department-list')
    return render(request, 'core/department_confirm_delete.html', {'department': department})

# Bank Account views
@login_required
def bank_account_list(request):
    bank_accounts = BankAccount.objects.all()
    return render(request, 'core/bank_account_list.html', {'bank_accounts': bank_accounts})

@login_required
def bank_account_create(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            bank_account = form.save()
            # Notify everyone
            users = CustomUser.objects.all()
            create_notifications(
                recipients=list(users),
                message=f"A new bank account '{bank_account.bank_name}' has been added.",
                notif_type='info',
                actor=request.user
            )
            return redirect('bank-account-list')
    else:
        form = BankAccountForm()
    return render(request, 'core/bank_account_form.html', {'form': form, 'title': 'Add Bank Account'})

@login_required
def bank_account_update(request, pk):
    bank_account = get_object_or_404(BankAccount, pk=pk)
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=bank_account)
        if form.is_valid():
            form.save()
            # Notify everyone
            users = CustomUser.objects.all()
            create_notifications(
                recipients=list(users),
                message=f"Bank account '{bank_account.bank_name}' was updated.",
                notif_type='info',
                actor=request.user
            )
            return redirect('bank-account-list')
    else:
        form = BankAccountForm(instance=bank_account)
    return render(request, 'core/bank_account_form.html', {'form': form, 'bank_account': bank_account, 'title': 'Edit Bank Account'})

@login_required
def bank_account_delete(request, pk):
    bank_account = get_object_or_404(BankAccount, pk=pk)
    if request.method == 'POST':
        bank_account.delete()
        return redirect('bank-account-list')
    return render(request, 'core/bank_account_confirm_delete.html', {'bank_account': bank_account})

# Role views
@login_required
def role_list(request):
    roles = Role.objects.all()
    return render(request, 'core/role_list.html', {'roles': roles})

@login_required
def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            # Notify everyone
            return redirect('role-list')
    else:
        form = RoleForm()
    return render(request, 'core/role_form.html', {'form': form, 'title': 'Add Role'})

@login_required
def role_update(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect('role-list')
    else:
        form = RoleForm(instance=role)
    return render(request, 'core/role_form.html', {'form': form, 'role': role, 'title': 'Edit Role'})

@login_required
def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        return redirect('role-list')
    return render(request, 'core/role_confirm_delete.html', {'role': role})

# User Profile Views
@login_required
def user_profile(request):
    """User profile view for individual users"""
    return render(request, 'core/user_profile.html', {
        'user': request.user
    })

@login_required
def user_profile_edit(request):
    """Edit user profile view"""
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        # Notify user and admins
        admins = CustomUser.objects.filter(is_staff=True)
        recipients = set([user] + list(admins))
        create_notifications(
            recipients=list(recipients),
            message=f"User '{user.username}' updated their profile.",
            notif_type='info',
            actor=user
        )
        messages.success(request, 'Profile updated successfully!')
        return redirect('user-profile')
    return render(request, 'core/user_profile_edit.html', {
        'user': request.user
    })

@login_required
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user-profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/change_password.html', {
        'form': form
    })

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    if request.method == 'POST':
        notifications.update(is_read=True)
    return render(request, 'core/notifications_list.html', {'notifications': notifications})

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def clear_all_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

# CustomUser Management Views
@login_required
@staff_member_required
def user_list(request):
    users = CustomUser.objects.all().order_by('username')
    return render(request, 'core/user_list.html', {'users': users})

@login_required
@staff_member_required
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Notify everyone
            users = CustomUser.objects.all()
            create_notifications(
                recipients=list(users),
                message=f"A new user '{user.username}' has been created.",
                notif_type='info',
                actor=request.user
            )
            messages.success(request, f'User "{user.username}" has been created successfully!')
            return redirect('user-list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Add User'})

@login_required
@staff_member_required
def user_update(request, pk):
    """Update an existing user"""
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Notify everyone
            create_notifications(
                recipients=[request.user],
                message=f"Your profile is updated.",
                notif_type='info',
                actor=request.user
            )
            messages.success(request, f'User "{user.username}" has been updated successfully!')
            return redirect('user-list')
    else:
        form = CustomUserUpdateForm(instance=user)
    return render(request, 'core/user_form.html', {'form': form, 'user': user, 'title': 'Edit User'})

@login_required
@staff_member_required
def user_delete(request, pk):
    """Delete a user"""
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        # Notify everyone
        users = CustomUser.objects.all()
        create_notifications(
            recipients=list(users),
            message=f"User '{username}' was deleted.",
            notif_type='warning',
            actor=request.user
        )
        messages.success(request, f'User "{username}" has been deleted successfully!')
        return redirect('user-list')
    return render(request, 'core/user_confirm_delete.html', {'user': user})

@login_required
@staff_member_required
def user_change_password(request, pk):
    """Change user password"""
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password for "{user.username}" has been changed successfully!')
            return redirect('user-list')
    else:
        form = CustomUserPasswordForm(user)
    return render(request, 'core/user_change_password.html', {'form': form, 'user': user})

@login_required
@staff_member_required
def user_detail(request, pk):
    """View user details"""
    user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'core/user_detail.html', {'user': user})
