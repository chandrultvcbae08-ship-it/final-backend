from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PatientProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'is_deleted', 'created_at_display')
    list_filter = ('role', 'is_active', 'is_deleted')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone')}),
        ('Roles & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_deleted', 'deleted_at')}),
    )
    search_fields = ('email', 'full_name')
    ordering = ('email',)

    def created_at_display(self, obj):
        return obj.date_joined


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'blood_group', 'emergency_contact')
    search_fields = ('user__full_name', 'user__email')
