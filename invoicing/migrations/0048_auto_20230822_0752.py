# Generated by Django 3.1.4 on 2023-08-22 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0047_auto_20230803_1004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuingcompanyname',
            name='sifen_economic_activity_code',
            field=models.CharField(max_length=10, null=True, verbose_name='SIFEN ECONOMIC ACTIVITY CODE'),
        ),
    ]
