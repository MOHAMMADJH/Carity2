from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import User

class SocialMediaMixin(models.Model):
    """نموذج مشترك لإعدادات النشر على وسائل التواصل الاجتماعي"""
    social_publish = models.BooleanField(default=False, verbose_name="نشر على وسائل التواصل")
    facebook_enabled = models.BooleanField(default=False, verbose_name="نشر على فيسبوك")
    twitter_enabled = models.BooleanField(default=False, verbose_name="نشر على تويتر")
    instagram_enabled = models.BooleanField(default=False, verbose_name="نشر على انستقرام")
    whatsapp_enabled = models.BooleanField(default=False, verbose_name="نشر على واتساب")
    telegram_enabled = models.BooleanField(default=False, verbose_name="نشر على تلقرام")
    
    social_image = models.ImageField(
        upload_to='social_media/',
        null=True,
        blank=True,
        verbose_name="صورة للنشر الاجتماعي"
    )
    social_description = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="وصف للنشر الاجتماعي"
    )
    
    last_social_publish = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="آخر نشر اجتماعي"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.social_publish and not self.last_social_publish:
            self.last_social_publish = timezone.now()
        super().save(*args, **kwargs)

class Charity(SocialMediaMixin, models.Model):
    name = models.CharField(_("اسم الجمعية"), max_length=255)
    description = models.TextField(_("وصف الجمعية"))
    logo = models.ImageField(_("شعار الجمعية"), upload_to='charity_logos/', null=True, blank=True)
    address = models.TextField(_("العنوان"))
    phone = models.CharField(_("رقم الهاتف"), max_length=20)
    email = models.EmailField(_("البريد الإلكتروني"))
    website = models.URLField(_("الموقع الإلكتروني"), blank=True, null=True)
    is_active = models.BooleanField(_("نشط"), default=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("جمعية خيرية")
        verbose_name_plural = _("جمعيات خيرية")

    def __str__(self):
        return self.name

class CharityAssistanceLink(SocialMediaMixin, models.Model):
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name='assistance_links', verbose_name=_("الجمعية"))
    title = models.CharField(_("عنوان الرابط"), max_length=255)
    url = models.URLField(_("الرابط"))
    description = models.TextField(_("وصف الرابط"), blank=True, null=True)
    is_active = models.BooleanField(_("نشط"), default=True)
    created_at = models.DateTimeField(_("تاريخ الإنشاء"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)

    class Meta:
        verbose_name = _("رابط مساعدة")
        verbose_name_plural = _("روابط المساعدة")
        ordering = ['created_at']

    def __str__(self):
        return f"{self.charity.name} - {self.title}"

class AidType(models.Model):
    name = models.CharField(_("نوع المساعدة"), max_length=100)
    description = models.TextField(_("وصف المساعدة"))
    icon = models.CharField(_("أيقونة"), max_length=50, blank=True)  # لتخزين اسم الأيقونة من مكتبة الأيقونات

    class Meta:
        verbose_name = _("نوع مساعدة")
        verbose_name_plural = _("أنواع المساعدات")

    def __str__(self):
        return self.name

class AidRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', _('قيد الانتظار')),
        ('approved', _('تمت الموافقة')),
        ('rejected', _('مرفوض')),
        ('completed', _('مكتمل')),
    ]
    MARITAL_STATUS_CHOICES = [
    ('single', _('أعزب/عزباء')),
    ('married', _('متزوج/ة')),
    ('divorced', _('مطلق/ة')),
    ('widowed', _('أرمل/ة')),
]
    # Basic Information
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, verbose_name=_("الجمعية"))
    aid_type = models.ForeignKey(AidType, on_delete=models.CASCADE, verbose_name=_("نوع المساعدة"))
    requester = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("مقدم الطلب"))
    status = models.CharField(_("حالة الطلب"), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Beneficiary Information
    full_name = models.CharField(_("اسم المستفيد"), max_length=255)
    is_guardian = models.BooleanField(_("هل أنت ولي الأمر؟"), default=False)
    id_number = models.CharField(_("رقم الهوية"), max_length=20)
    
    # Family Information
    marital_status = models.CharField(
    _("الحالة الاجتماعية"),
    max_length=20,
    choices=MARITAL_STATUS_CHOICES,
    default='single')   
    wife_name = models.CharField(_("اسم الزوجة"), max_length=255, blank=True, null=True)
    wife_id_number = models.CharField(_("رقم هوية الزوجة"), max_length=20, blank=True, null=True)
    family_members = models.PositiveIntegerField(_("عدد أفراد الأسرة"), default=1)
    male_count = models.PositiveIntegerField(_("عدد الذكور مع الأب"), default=0)
    female_count = models.PositiveIntegerField(_("عدد الإناث مع الأم"), default=0)

    # Pregnancy and Children Information
    is_wife_pregnant = models.BooleanField(_("هل الزوجة حامل؟"), default=False)
    is_wife_nursing = models.BooleanField(_("هل الزوجة مرضعة؟"), default=False)
    infants_count = models.PositiveIntegerField(_("عدد الأطفال الرضع"), default=0)
    children_under_two = models.PositiveIntegerField(_("عدد الأطفال أقل من سنتين"), default=0)
    children_two_to_five = models.PositiveIntegerField(_("عدد الأطفال من سنتين إلى 5 سنوات"), default=0)
    children_above_five = models.PositiveIntegerField(_("عدد الأطفال أكبر من 5 سنوات"), default=0)
    
    # Health and Additional Information
    health_status = models.TextField(_("الحالة الصحية للأفراد"), blank=True)
    additional_info = models.TextField(_("معلومات إضافية"), blank=True)
    urgent = models.BooleanField(_("حالة طارئة"), default=False)
    documents = models.FileField(_("المستندات الداعمة"), upload_to='aid_documents/', null=True, blank=True)
    notes = models.TextField(_("ملاحظات"), blank=True)
    
    # Displacement Information
    current_residence = models.CharField(_("مكان السكن الحالي"), max_length=255, default="غير محدد")
    previous_residence = models.CharField(_("مكان السكن السابق"), max_length=255, default="غير محدد")
    displacement_reason = models.TextField(_("سبب النزوح"), blank=True)
    
    # Meta Information
    created_at = models.DateTimeField(_("تاريخ التقديم"), auto_now_add=True)
    updated_at = models.DateTimeField(_("تاريخ التحديث"), auto_now=True)
    completed_at = models.DateTimeField(_("تاريخ الإكمال"), null=True, blank=True)

    class Meta:
        verbose_name = _("طلب مساعدة")
        verbose_name_plural = _("طلبات المساعدة")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.aid_type.name}"

class CharityNews(SocialMediaMixin, models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان الخبر")
    content = models.TextField(verbose_name="محتوى الخبر")
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, verbose_name="الجمعية")
    publication_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ النشر")
    image = models.ImageField(upload_to='news_images/', null=True, blank=True, verbose_name="صورة الخبر")
    is_breaking = models.BooleanField(default=False, verbose_name="خبر عاجل")
    is_important = models.BooleanField(default=False, verbose_name="خبر مهم")
    important_until = models.DateTimeField(null=True, blank=True, verbose_name="مهم حتى تاريخ")
    tags = models.CharField(max_length=500, blank=True, verbose_name="الوسوم", help_text="أدخل الوسوم مفصولة بفواصل")
    views_count = models.PositiveIntegerField(default=0, verbose_name="عدد المشاهدات")
    last_viewed = models.DateTimeField(auto_now=True, verbose_name="آخر مشاهدة")
    telegram_enabled = models.BooleanField(default=False, verbose_name='النشر على تلجرام')
    instagram_enabled = models.BooleanField(default=False, verbose_name='النشر على انستقرام')

    class Meta:
        ordering = ['-publication_date']
        verbose_name = "خبر"
        verbose_name_plural = "أخبار"

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views_count += 1
        self.save()

    def get_tags_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('charities:news_detail', kwargs={'pk': self.pk})
