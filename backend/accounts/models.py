from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Organization(models.Model):
    name = models.CharField(max_length=255, null=False)
    status = models.IntegerField(default=0, null=False)
    personal = models.BooleanField(default=False, null=True)
    settings = models.JSONField(default=dict, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updated on save

    def __str__(self):
        return self.name

class User(AbstractUser):
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=255, null=False)
    profile = models.JSONField(default=dict, null=False)
    status = models.IntegerField(default=0, null=False)
    settings = models.JSONField(default=dict, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updated on save

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password', 'username']

    def __str__(self):
        return self.email

class Role(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Member(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    settings = models.JSONField(default=dict, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updated on save

    def __str__(self):
        return f'{self.user.email} in {self.org.name}'
