from django.contrib import admin
from .models import User, Profile
from django.contrib.auth.admin import UserAdmin

# Register your models here.


class UserAdminConfig(UserAdmin):
    model = User
    search_fields = ('email',)
    list_filter = ('email', 'is_active', 'is_staff')
    ordering = ('email', 'first_name', 'last_name')
    list_display = ('email', 'uuid', 'date_joined', 'is_active', 'is_staff')
    fieldsets = (
        ('Credentials', {'fields': ('first_name',
         'last_name', 'email')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
         'is_superuser', 'last_login', 'date_joined', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff')}
         ),
    )


admin.site.register(User, UserAdminConfig)
admin.site.register(Profile)
