# Generated by Django 3.1.4 on 2021-03-24 19:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduling', '0003_auto_20210322_1711'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='canceled_by',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='filed_by',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='scheduled_by',
        ),
        migrations.CreateModel(
            name='AppointmentStateUserLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('state_log_datetime', models.DateTimeField(auto_now=True, verbose_name='State log datetime')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointment_states_user_logs', to='scheduling.appointment', verbose_name='Appointment')),
                ('appointment_state', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointment_states_user_logs', to='scheduling.appointmentstate', verbose_name='Appointment State')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointment_states_user_logs', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Appointment State User Log',
                'verbose_name_plural': 'Appointments States User Logs',
            },
        ),
    ]
