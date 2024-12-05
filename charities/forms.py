from django import forms
from .models import Charity

class CharityForm(forms.ModelForm):
    class Meta:
        model = Charity
        fields = ['name', 'description', 'logo', 'address', 'phone', 'email', 'website', 'is_active']

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import AidRequest

class AidRequestForm(forms.ModelForm):
    class Meta:
        model = AidRequest
        fields = [
            # Basic Information
            'charity', 'aid_type',
            
            # Beneficiary Information
            'full_name', 'is_guardian', 'id_number',
            
            # Family Information
            'marital_status', 'wife_name', 'wife_id_number',
            'family_members', 'male_count', 'female_count',
            
            # Pregnancy and Children Information
            'is_wife_pregnant', 'is_wife_nursing', 'infants_count',
            
            # Children Age Details
            'children_under_two', 'children_two_to_five', 'children_above_five',
            
            # Health Information
            'health_status', 'additional_info',
            
            # Displacement Information
            'current_residence', 'previous_residence', 'displacement_reason',
        ]
        
        widgets = {
            'marital_status': forms.Select(choices=[
                ('single', _('أعزب')),
                ('married', _('متزوج')),
                ('divorced', _('مطلق')),
                ('widowed', _('أرمل')),
            ]),
            'health_status': forms.Textarea(attrs={'rows': 4}),
            'additional_info': forms.Textarea(attrs={'rows': 4}),
            'displacement_reason': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required
        required_fields = [
            'full_name', 'id_number', 'family_members',
            'male_count', 'female_count', 'current_residence'
        ]
        for field in required_fields:
            self.fields[field].required = True
        
        # Make wife-related fields conditional
        wife_fields = ['wife_name', 'wife_id_number', 'is_wife_pregnant', 'is_wife_nursing']
        for field in wife_fields:
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        marital_status = cleaned_data.get('marital_status')
        wife_name = cleaned_data.get('wife_name')
        wife_id_number = cleaned_data.get('wife_id_number')

        # Validate wife information if married
        if marital_status == 'married':
            if not wife_name:
                self.add_error('wife_name', _('يجب إدخال اسم الزوجة للمتزوجين'))
            if not wife_id_number:
                self.add_error('wife_id_number', _('يجب إدخال رقم هوية الزوجة للمتزوجين'))

        # Validate children counts
        total_children = (
            cleaned_data.get('children_under_two', 0) +
            cleaned_data.get('children_two_to_five', 0) +
            cleaned_data.get('children_above_five', 0)
        )
        if total_children != cleaned_data.get('infants_count', 0):
            self.add_error('infants_count', _('مجموع الأطفال في الفئات العمرية يجب أن يساوي العدد الإجمالي للأطفال'))

        return cleaned_data


from django import forms
from .models import Charity

class CharityForm(forms.ModelForm):
    class Meta:
        model = Charity
        fields = ['name', 'description', 'logo', 'address', 'phone', 'email', 'website', 'is_active']

from django import forms
from .models import CharityNews

class CharityNewsForm(forms.ModelForm):
    class Meta:
        model = CharityNews
        fields = [
            'title', 'content', 'charity', 'image', 
            'is_breaking', 'is_important', 'important_until', 'tags',
            'telegram_enabled', 'instagram_enabled'
        ]
        widgets = {
            'important_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'content': forms.Textarea(attrs={'rows': 5}),
            'telegram_enabled': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'instagram_enabled': forms.CheckboxInput(attrs={'class': 'form-checkbox'})
        }
        labels = {
            'title': 'عنوان الخبر',
            'content': 'محتوى الخبر',
            'charity': 'الجمعية',
            'image': 'صورة الخبر',
            'is_breaking': 'خبر عاجل',
            'is_important': 'خبر مهم',
            'important_until': 'مهم حتى تاريخ',
            'tags': 'الوسوم',
            'telegram_enabled': 'نشر على تلجرام',
            'instagram_enabled': 'نشر على انستقرام'
        }

from django import forms
from .models import CharityAssistanceLink

class CharityAssistanceLinkForm(forms.ModelForm):
    class Meta:
        model = CharityAssistanceLink
        fields = ['charity', 'title', 'url', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان الرابط'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف الرابط'}),
            'charity': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SocialMediaSettingsForm(forms.Form):
    """نموذج إعدادات النشر على وسائل التواصل الاجتماعي"""
    social_publish = forms.BooleanField(required=False, label="تفعيل النشر الاجتماعي")
    facebook_enabled = forms.BooleanField(required=False, label="نشر على فيسبوك")
    twitter_enabled = forms.BooleanField(required=False, label="نشر على تويتر")
    instagram_enabled = forms.BooleanField(required=False, label="نشر على انستقرام")
    whatsapp_enabled = forms.BooleanField(required=False, label="نشر على واتساب")
    telegram_enabled = forms.BooleanField(required=False, label="نشر على تلقرام")
    
    social_image = forms.ImageField(required=False, label="صورة للنشر الاجتماعي")
    social_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False,
        label="وصف للنشر الاجتماعي",
        max_length=500
    )
