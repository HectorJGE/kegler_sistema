# Generated by Django 3.1.4 on 2022-01-13 01:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0023_auto_20211221_1124'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issuingcompanyname',
            options={'verbose_name': 'Company Name', 'verbose_name_plural': 'Company Name'},
        ),
        migrations.AlterModelOptions(
            name='stamprange',
            options={'verbose_name': 'StampRange', 'verbose_name_plural': 'StampRange'},
        ),
    ]