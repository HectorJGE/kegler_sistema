# Generated by Django 3.1.4 on 2023-09-13 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0065_auto_20230913_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='customer_type',
            field=models.IntegerField(choices=[(1, 'Individual'), (2, 'Legal Entity')], default=1, null=True, verbose_name='Customer Type'),
        ),
    ]
