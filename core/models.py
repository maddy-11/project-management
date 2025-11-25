from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.

class CompanyProfile(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return self.name

class BankAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('savings', 'Savings'),
        ('current', 'Current'),
        ('business', 'Business'),
        ('investment', 'Investment'),
    ]
    
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=255)
    branch_code = models.CharField(max_length=10, blank=True, null=True)
    bank_code = models.CharField(max_length=10, blank=True, null=True)
    branch_address = models.CharField(max_length=100, blank=True, null=True)
    swift_code = models.CharField(max_length=20, blank=True, null=True)
    iban = models.CharField(max_length=50, blank=True, null=True)
    NTN = models.CharField(max_length=30, blank=True, null=True)
    STRN = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['bank_name', 'account_holder_name']

    def __str__(self):
        return f"{self.bank_name} - {self.account_holder_name} ({self.account_number})"

class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    manager = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    page_access = models.JSONField(default=list, blank=True)  # List of allowed page names/IDs
    partners = models.ManyToManyField('clients.Partner', related_name='roles',blank=True)
    partner_based = models.BooleanField(default=False)
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]
    recipient = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='actor_notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    # Optional: generic relation to any object
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        recipient_name = self.recipient.username if self.recipient else 'Unknown recipient'
        return f"Notification for {recipient_name}: {self.message}"
