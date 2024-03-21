# Generated by Django 3.1.4 on 2021-03-23 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultation', '0015_auto_20210323_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='consultationsheet',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Contact Email'),
        ),
        migrations.AddField(
            model_name='consultationsheet',
            name='contact_number',
            field=models.CharField(default='0986210344', max_length=15, verbose_name='Contact Number'),
            preserve_default=False,
        ),
    ]
