# Generated by Django 4.2.7 on 2024-12-02 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charities', '0004_charitynews_important_until_charitynews_is_important'),
    ]

    operations = [
        migrations.AddField(
            model_name='charitynews',
            name='is_breaking',
            field=models.BooleanField(default=False, verbose_name='خبر عاجل'),
        ),
    ]
