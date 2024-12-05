from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', _('ذكر')),
        ('F', _('أنثى')),
    ]

    USER_TYPE_CHOICES = [
        ('beneficiary', _('مستفيد')),
        ('charity_admin', _('مدير جمعية')),
        ('system_admin', _('مدير نظام')),
    ]

    # معلومات شخصية إضافية
    phone_number = models.CharField(_("رقم الهاتف"), max_length=20, blank=True)
    national_id = models.CharField(_("رقم الهوية الوطنية"), max_length=20, unique=True)
    gender = models.CharField(_("الجنس"), max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField(_("تاريخ الميلاد"), null=True, blank=True)
    address = models.TextField(_("العنوان"), blank=True)
    
    # نوع المستخدم
    user_type = models.CharField(
        _("نوع المستخدم"),
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='beneficiary'
    )
    
    # الجمعية المرتبطة (إذا كان مدير جمعية)
    charity = models.ForeignKey(
        'charities.Charity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("الجمعية"),
        related_name='administrators'
    )

    # الحالة
    is_active = models.BooleanField(_("نشط"), default=True)
    created_at = models.DateTimeField(_("تاريخ التسجيل"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("مستخدم")
        verbose_name_plural = _("المستخدمون")

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

    def is_charity_admin(self):
        return self.user_type == 'charity_admin'

    def is_system_admin(self):
        return self.user_type == 'system_admin'

    def is_beneficiary(self):
        return self.user_type == 'beneficiary'