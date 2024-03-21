from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from scheduling.models import Schedule, Appointment, DefaultDoctorAppointmentSchedule, AppointmentState, \
    AppointmentStateUserLog, AppointmentDocumentType


# ################################### SCHEDULE
class ScheduleResource(resources.ModelResource):

    class Meta:
        model = Schedule


class ScheduleAdmin(ImportExportModelAdmin):
    resource_class = ScheduleResource
    search_fields = ['id', 'doctor__name', 'doctor__last_name']
    list_filter = ['canceled', 'schedule_date', 'start_time', 'end_time', 'created_at', 'updated_at']

    list_display = (
        'id',
        'schedule_date',
        'start_time',
        'end_time',
        'doctor',
        'canceled',
        'created_at',
        'updated_at'
    )


admin.site.register(Schedule, ScheduleAdmin)


# ############################### APPOINTMENT
class AppointmentResource(resources.ModelResource):

    class Meta:
        model = Appointment


class AppointmentAdmin(ImportExportModelAdmin):
    resource_class = AppointmentResource
    search_fields = ['id', 'patient__name', 'doctor__name', 'medical_study__name', 'medical_equipment__name', 'appointment_state__name', 'insurance_plan__name']
    list_filter = ['appointment_state', 'appointment_date_start', 'appointment_date_end', 'insurance_plan', 'currency', 'created_at', 'updated_at']

    list_display = (
        'id',
        'patient',
        'contact_number',
        'contact_email',
        'medical_study',
        'medical_equipment',
        'appointment_date_start',
        'appointment_date_end',
        'doctor',
        'appointment_state',
        'insurance_plan',
        'currency',
        'created_at',
        'updated_at'
    )


admin.site.register(Appointment, AppointmentAdmin)


# ################################ DEFAULT DOCTOR APPOINTMENT SCHEDULE
class DefaultDoctorAppointmentScheduleResource(resources.ModelResource):

    class Meta:
        model = DefaultDoctorAppointmentSchedule


class DefaultDoctorAppointmentScheduleAdmin(ImportExportModelAdmin):
    resource_class = DefaultDoctorAppointmentScheduleResource
    search_fields = ['id', 'doctor__name', 'doctor__last_name']
    list_filter = ['day', 'start_time', 'end_time', 'created_at', 'updated_at']

    list_display = (
        'id',
        'doctor',
        'day',
        'start_time',
        'end_time',
        'created_at',
        'updated_at'
    )


admin.site.register(DefaultDoctorAppointmentSchedule, DefaultDoctorAppointmentScheduleAdmin)


# ############################### APPOINTMENT STATE
class AppointmentStateResource(resources.ModelResource):

    class Meta:
        model = AppointmentState


class AppointmentStateAdmin(ImportExportModelAdmin):
    resource_class = AppointmentStateResource
    search_fields = ['id', 'name']
    list_filter = ['state_code', 'created_at', 'updated_at']

    list_display = (
        'id',
        'name',
        'state_code',
        'created_at',
        'updated_at'
    )


admin.site.register(AppointmentState, AppointmentStateAdmin)


# Default Doctor Appointment Schedule Inline
class DefaultDoctorAppointmentScheduleInlineAdmin(admin.TabularInline):
    model = DefaultDoctorAppointmentSchedule
    extra = 0


# Doctor Medical Equipment Schedule Inline
class ScheduleInlineAdmin(admin.TabularInline):
    model = Schedule
    extra = 0


# ############################### APPOINTMENT STATE USER LOG
class AppointmentStateUserLogResource(resources.ModelResource):

    class Meta:
        model = AppointmentStateUserLog


class AppointmentStateUserLogAdmin(ImportExportModelAdmin):
    resource_class = AppointmentStateResource
    search_fields = ['id', 'appointment__patient__name', 'appointment__patient__last_name', 'appointment_state__name', 'user__username']
    list_filter = ['appointment_state', 'user', 'created_at', 'updated_at']

    list_display = (
        'id',
        'appointment',
        'appointment_state',
        'user',
        'state_log_datetime',
        'created_at',
        'updated_at'
    )


admin.site.register(AppointmentStateUserLog, AppointmentStateUserLogAdmin)


# ############################### APPOINTMENT DOCUMENT TYPE
class AppointmentDocumentTypeResource(resources.ModelResource):

    class Meta:
        model = AppointmentDocumentType


class AppointmentDocumentTypeAdmin(ImportExportModelAdmin):
    resource_class = AppointmentDocumentTypeResource
    search_fields = ['id', 'name']
    list_filter = ['id', 'created_at', 'updated_at']

    list_display = (
        'id',
        'name',
        'created_at',
        'updated_at'
    )


admin.site.register(AppointmentDocumentType, AppointmentDocumentTypeAdmin)