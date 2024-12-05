from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class UserRegistrationForm(UserCreationForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input rounded-md'}),
        label=_('تاريخ الميلاد')
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'phone_number', 'national_id', 'gender', 'birth_date',
            'address', 'password1', 'password2'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تخصيص رسائل المساعدة
        self.fields['username'].help_text = _('مطلوب. 150 حرف أو أقل. يمكن استخدام الحروف والأرقام و @/./+/-/_ فقط.')
        self.fields['password1'].help_text = _('كلمة المرور يجب أن تكون على الأقل 8 أحرف.')
        self.fields['password2'].help_text = _('أدخل نفس كلمة المرور للتأكيد.')
        
        # إضافة الفئات لجميع الحقول
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input rounded-md'