# Generated by Django 3.1.4 on 2021-03-17 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultation', '0006_auto_20210317_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultationsheet',
            name='discount',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Discount'),
        ),
    ]