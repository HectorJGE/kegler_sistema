# Generated by Django 3.1.4 on 2023-09-03 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0026_auto_20210812_0926'),
    ]

    operations = [
        migrations.AddField(
            model_name='insurancecompany',
            name='address',
            field=models.CharField(max_length=250, null=True, verbose_name='Address'),
        ),
        migrations.AddField(
            model_name='insurancecompany',
            name='email',
            field=models.EmailField(max_length=254, null=True, verbose_name='Email'),
        ),
    ]
