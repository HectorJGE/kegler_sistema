# Generated by Django 3.1.4 on 2023-09-04 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0027_auto_20230903_1927'),
    ]

    operations = [
        migrations.AddField(
            model_name='insurancecompany',
            name='phone_number',
            field=models.CharField(max_length=20, null=True, verbose_name='Phone Number'),
        ),
    ]
