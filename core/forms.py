from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Department, Role, BankAccount, CustomUser

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter department description'
            }),
            'manager': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department manager'
            }),
        }

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_number', 'account_holder_name', 
                 'branch_code', 'branch_address', 'bank_code', 'swift_code', 'iban', 'NTN', 'STRN', 'is_active', 'notes']
        widgets = {
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bank name'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account number'
            }),
            'account_holder_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account holder name'
            }),
            'branch_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter branch code (optional)'
            }),
            'branch_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter branch address (optional)'
            }),
            'bank_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bank code (optional)'
            }),
            'swift_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter SWIFT code (optional)'
            }),
            'iban': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter IBAN (optional)'
            }),
            'NTN': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter NTN (optional)'
            }),
            'STRN': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter STRN (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any additional notes'
            }),
        }

class RoleForm(forms.ModelForm):
    PAGE_GROUPED_CHOICES = [
        ("Dashboard", [
            ("dashboard", "Dashboard"),
        ]),
        ("Company Details", [
            ("company-profile", "Company Profile"),
            ("department-list", "Departments"),
            ("bank-account-list", "Bank Accounts"),
            ("documents", "Documents"),
            ("role-list", "Roles"),
            ("user-list", "Users"),
        ]),
        ("CRM Management", [
            ("crm-info", "CRM Info"),
            ("pipelines", "Pipelines"),
            ("lead-search", "Lead Search"),
            ("prospects", "Prospects"),
        ]),
        ("Client Management", [
            ("partners", "Partners"),
            ("referrer", "Referrer"),
            ("projects", "Projects"),
        ]),
        ("Invoice Management", [
            ("invoices", "Invoices"),
        ]),
        ("Employee Details", [
            ("employees", "Employee"),
            ("salary", "Salary"),
        ]),
        ("Office Expenses", [
            ("expenses", "Expenses/Budget"),
            ("data-summary", "Summary"),
        ]),
        ("Assets Management", [
            ("assets", "Assets Management")
        ]),
        ("Reports", [
            ("reports", "Reports"),
        ]),
    ]
    page_access = forms.MultipleChoiceField(
        choices=PAGE_GROUPED_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Page Access',
        help_text='Select the pages this role can access.'
    )
    partners = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        label='Partners',
        help_text='Select the partners this role can access.',
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select partners...',
            'multiple': 'multiple'
        })
    )
    partner_based = forms.BooleanField(
        required=False,
        label='Partner-Based Access',
        help_text='Enable this to restrict access based on selected partners.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-bs-toggle': 'toggle',
            'data-bs-onstyle': 'success',
            'data-bs-offstyle': 'secondary',
            'data-on': 'Enabled',
            'data-off': 'Disabled'
        })
    )

    pipelines = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        label='Pipelines',
        help_text='Select the pipelines this role can access.',
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'data-placeholder': 'Select pipelines...',
            'multiple': 'multiple'
        })
    )
    pipeline_based = forms.BooleanField(
        required=False,
        label='Pipeline-Based Access',
        help_text='Enable this to restrict access based on selected pipelines.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'data-bs-toggle': 'toggle',
            'data-bs-onstyle': 'success',
            'data-bs-offstyle': 'secondary',
            'data-on': 'Enabled',
            'data-off': 'Disabled'
        })
    )

    class Meta:
        model = Role
        fields = ['name', 'description', 'page_access', 'partner_based', 'partners', 'pipeline_based', 'pipelines']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the queryset for partners
        from clients.models import Partner
        self.fields['partners'].queryset = Partner.objects.all().order_by('name')
        # Set the queryset for pipelines
        from crm.models import Pipeline
        self.fields['pipelines'].queryset = Pipeline.objects.all().order_by('name')
        
        if self.instance and self.instance.pk:
            self.fields['page_access'].initial = self.instance.page_access or []

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.page_access = self.cleaned_data.get('page_access', [])
        if commit:
            instance.save()
            # Save many-to-many relationships
            self.save_m2m()
        return instance 

class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        empty_label="Select a role (optional)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label='Active',
        help_text='Designates whether this user should be treated as active.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CustomUserUpdateForm(UserChangeForm):
    """Form for updating existing users"""
    password = None  # Remove password field from update form
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        empty_label="Select a role (optional)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=False,
        label='Active',
        help_text='Designates whether this user should be treated as active.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_superuser = forms.BooleanField(
        required=False,
        label='Superuser Status',
        help_text='Designates that this user has all permissions without explicitly assigning them.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_superuser')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})

class CustomUserPasswordForm(forms.Form):
    """Form for changing user password"""
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Your password must contain at least 8 characters."
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter the same password as before, for verification."
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user