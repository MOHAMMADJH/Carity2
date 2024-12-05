from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active', 'gender')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'national_id')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('المعلومات الشخصية'), {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number',
                'national_id', 'gender', 'birth_date', 'address'
            )
        }),
        (_('نوع المستخدم'), {
            'fields': ('user_type', 'charity')
        }),
        (_('الصلاحيات'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('تواريخ مهمة'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('المعلومات الشخصية'), {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number',
                'national_id', 'gender', 'birth_date', 'address'
            )
        }),
        (_('نوع المستخدم'), {
            'fields': ('user_type', 'charity')
        }),
    )

    readonly_fields = ('created_at', 'updated_at')