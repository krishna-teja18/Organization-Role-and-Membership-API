from django.contrib import admin
from .models import User, Organization, Member, Role

# Admin configuration for User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'status', 'created_at', 'updated_at')
    search_fields = ('email',)
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')

# Admin configuration for Organization model
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'personal', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('status', 'personal')
    readonly_fields = ('created_at', 'updated_at')

# Admin configuration for Member model
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('org', 'user', 'role', 'status', 'created_at', 'updated_at')
    search_fields = ('user__email', 'org__name')
    list_filter = ('status', 'role', 'org')
    readonly_fields = ('created_at', 'updated_at')

# Admin configuration for Role model
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'org')
    search_fields = ('name', 'description')
    list_filter = ('org',)
