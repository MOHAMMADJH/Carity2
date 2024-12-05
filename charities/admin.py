from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Charity, AidType, AidRequest, CharityNews, CharityAssistanceLink

class CharityAssistanceLinkInline(admin.TabularInline):
    model = CharityAssistanceLink
    extra = 1

@admin.register(Charity)
class CharityAdmin(admin.ModelAdmin):
    inlines = [CharityAssistanceLinkInline]
    list_display = ('name', 'email', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(AidType)
class AidTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

from django.contrib import admin
from .models import AidRequest

@admin.register(AidRequest)
class AidRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'id_number', 'status', 'created_at']
    list_filter = ['status', 'is_guardian', 'is_wife_pregnant', 'is_wife_nursing']
    search_fields = ['full_name', 'id_number', 'wife_name', 'wife_id_number']

admin.site.register(CharityAssistanceLink)

from .models import CharityNews

@admin.register(CharityNews)
class CharityNewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'charity', 'publication_date', 'is_breaking', 'is_important', 'views_count', 'tags')
    list_filter = ('charity', 'publication_date', 'is_breaking', 'is_important')
    search_fields = ('title', 'content', 'charity__name', 'tags')
    readonly_fields = ('views_count', 'last_viewed')
    fieldsets = (
        ('معلومات الخبر', {
            'fields': ('title', 'content', 'charity', 'image')
        }),
        ('تصنيف الخبر', {
            'fields': ('is_breaking', 'is_important', 'important_until', 'tags'),
            'description': 'يمكنك تحديد تصنيف الخبر والوسوم الخاصة به'
        }),
        ('إحصائيات', {
            'fields': ('views_count', 'last_viewed'),
            'description': 'إحصائيات مشاهدات الخبر'
        }),
    )