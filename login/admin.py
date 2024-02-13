from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Define a new User admin
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'proficiency_level', 'study_frequency', 'study_frequency_amount', 'portuguese_default') # Add your custom fields here
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Custom fields'), {'fields': ('proficiency_level', 'study_frequency', 'study_frequency_amount', 'portuguese_default')}), # This is where you add your custom fields
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'proficiency_level', 'study_frequency', 'study_frequency_amount', 'portuguese_default'), # Add your custom fields here
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

# Now register the new UserAdmin...
admin.site.register(CustomUser, CustomUserAdmin)

# Register your models here.
