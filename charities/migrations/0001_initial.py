# Generated by Django 4.2.7 on 2024-12-01 11:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AidType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='نوع المساعدة')),
                ('description', models.TextField(verbose_name='وصف المساعدة')),
                ('icon', models.CharField(blank=True, max_length=50, verbose_name='أيقونة')),
            ],
            options={
                'verbose_name': 'نوع مساعدة',
                'verbose_name_plural': 'أنواع المساعدات',
            },
        ),
        migrations.CreateModel(
            name='Charity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='اسم الجمعية')),
                ('description', models.TextField(verbose_name='وصف الجمعية')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='charity_logos/', verbose_name='شعار الجمعية')),
                ('address', models.TextField(verbose_name='العنوان')),
                ('phone', models.CharField(max_length=20, verbose_name='رقم الهاتف')),
                ('email', models.EmailField(max_length=254, verbose_name='البريد الإلكتروني')),
                ('website', models.URLField(blank=True, null=True, verbose_name='الموقع الإلكتروني')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'جمعية خيرية',
                'verbose_name_plural': 'جمعيات خيرية',
            },
        ),
        migrations.CreateModel(
            name='AidRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'قيد الانتظار'), ('approved', 'تمت الموافقة'), ('rejected', 'مرفوض'), ('completed', 'مكتمل')], default='pending', max_length=20, verbose_name='حالة الطلب')),
                ('full_name', models.CharField(max_length=255, verbose_name='اسم المستفيد')),
                ('is_guardian', models.BooleanField(default=False, verbose_name='هل أنت ولي الأمر؟')),
                ('id_number', models.CharField(max_length=20, verbose_name='رقم الهوية')),
                ('marital_status', models.CharField(max_length=20, verbose_name='الحالة الاجتماعية')),
                ('wife_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='اسم الزوجة')),
                ('wife_id_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='رقم هوية الزوجة')),
                ('family_members', models.PositiveIntegerField(default=1, verbose_name='عدد أفراد الأسرة')),
                ('male_count', models.PositiveIntegerField(default=0, verbose_name='عدد الذكور مع الأب')),
                ('female_count', models.PositiveIntegerField(default=0, verbose_name='عدد الإناث مع الأم')),
                ('is_wife_pregnant', models.BooleanField(default=False, verbose_name='هل الزوجة حامل؟')),
                ('is_wife_nursing', models.BooleanField(default=False, verbose_name='هل الزوجة مرضعة؟')),
                ('infants_count', models.PositiveIntegerField(default=0, verbose_name='عدد الأطفال الرضع')),
                ('children_under_two', models.PositiveIntegerField(default=0, verbose_name='عدد الأطفال أقل من سنتين')),
                ('children_two_to_five', models.PositiveIntegerField(default=0, verbose_name='عدد الأطفال من سنتين إلى 5 سنوات')),
                ('children_above_five', models.PositiveIntegerField(default=0, verbose_name='عدد الأطفال أكبر من 5 سنوات')),
                ('health_status', models.TextField(blank=True, verbose_name='الحالة الصحية للأفراد')),
                ('additional_info', models.TextField(blank=True, verbose_name='معلومات إضافية')),
                ('urgent', models.BooleanField(default=False, verbose_name='حالة طارئة')),
                ('documents', models.FileField(blank=True, null=True, upload_to='aid_documents/', verbose_name='المستندات الداعمة')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('current_residence', models.CharField(default='غير محدد', max_length=255, verbose_name='مكان السكن الحالي')),
                ('previous_residence', models.CharField(default='غير محدد', max_length=255, verbose_name='مكان السكن السابق')),
                ('displacement_reason', models.TextField(blank=True, verbose_name='سبب النزوح')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التقديم')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الإكمال')),
                ('aid_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='charities.aidtype', verbose_name='نوع المساعدة')),
                ('charity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='charities.charity', verbose_name='الجمعية')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='مقدم الطلب')),
            ],
            options={
                'verbose_name': 'طلب مساعدة',
                'verbose_name_plural': 'طلبات المساعدة',
                'ordering': ['-created_at'],
            },
        ),
    ]