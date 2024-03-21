import datetime
import os

from django.contrib.auth.models import User
from django.db import models
from softdelete.models import SoftDeleteObject
from django.utils.translation import ugettext_lazy as _
from auditlog.registry import auditlog

from base.models import Currency, TimeStampModel
from clinic.models import MedicalEquipment, Patient, MedicalStudy, Doctor, InsurancePlan, TreatingDoctor


def appointment_document_storage_path(instance, filename):
    return 'appointments/{0}/documents/{1}'.format(str(instance.appointment.id), filename)

# Create your models here.
# APPOINTMENT STATE
class AppointmentState(SoftDeleteObject, TimeStampModel):
    SCHEDULED_STATE = 0
    FILED_STATE = 1
    CANCELED_STATE = 2
    ABSENT_STATE = 3

    STATES_CODES = (
        (SCHEDULED_STATE, _('Scheduled')),
        (FILED_STATE, _('Filed')),
        (CANCELED_STATE, _('Canceled')),
        (ABSENT_STATE, _('Absent')),
    )
    name = models.CharField(max_length=50, verbose_name=_('Name'), null=False, blank=False)
    state_code = models.IntegerField(
        verbose_name=_('State code'),
        choices=STATES_CODES,
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('Appointment State')
        verbose_name_plural = _('Appointment States')

    def __str__(self):
        return self.name


auditlog.register(AppointmentState)


# Default Doctor Appointment Schedule
class DefaultDoctorAppointmentSchedule(SoftDeleteObject, TimeStampModel):
    DAYS_OF_THE_WEEK = (
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    )
    doctor = models.ForeignKey(
        to=Doctor, on_delete=models.PROTECT,
        null=False, blank=False,
        verbose_name=_('Doctor'),
        related_name='default_doctor_schedules'
    )
    day = models.IntegerField(
        verbose_name=_('Day of the week'),
        choices=DAYS_OF_THE_WEEK,
        null=False, blank=False
    )
    start_time = models.TimeField(
        verbose_name=_('Start Time'),
        null=False, blank=False
    )
    end_time = models.TimeField(
        verbose_name=_('End Time'),
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('Default Doctor Appointment Schedule')
        verbose_name_plural = _('Default Doctor Appointments Schedules')
        unique_together = ('doctor', 'day', 'start_time', 'end_time')

    def __str__(self):
        return str(self.doctor) + ' - ' + str(self.get_day_display()) + ' - ' + str(self.start_time) + ' to ' + str(self.end_time)


auditlog.register(DefaultDoctorAppointmentSchedule)


# SCHEDULE
class Schedule(SoftDeleteObject, TimeStampModel):
    schedule_date = models.DateField(
        verbose_name=_('Schedule Date'),
        null=False, blank=False,
    )
    start_time = models.TimeField(
        verbose_name=_('Start Time'),
        null=False, blank=False
    )
    end_time = models.TimeField(
        verbose_name=_('End Time'),
        null=False, blank=False
    )
    doctor = models.ForeignKey(
        to=Doctor, on_delete=models.PROTECT,
        verbose_name=_('Doctor'),
        null=False, blank=False,
        related_name='schedules'
    )
    canceled = models.BooleanField(
        verbose_name=_('Canceled'),
        default=False
    )

    class Meta:
        verbose_name = _('Schedule')
        verbose_name_plural = _('Schedules')

    def __str__(self):
        return _(self.schedule_date.strftime("%A")) + " " + self.schedule_date.strftime("%d/%m/%Y") + ' - ' + str(self.start_time) + ' to ' + str(self.end_time) + ' - ' + str(self.doctor)

    def delete(self, *args, **kwargs):
        # Set apointment state to Canceled
        self.canceled = True
        self.save()

    def save(self, *args, **kwargs):
        # If is an update
        if self.id:
            original_schedule = Schedule.objects.get(pk=self.id)
            original_start = datetime.datetime.combine(original_schedule.schedule_date, original_schedule.start_time)
            original_end = datetime.datetime.combine(original_schedule.schedule_date, original_schedule.end_time)
            appointments_in_original_schedule = Appointment.objects.filter(
                doctor=original_schedule.doctor,
                appointment_date__range=(original_start, original_end)
            )

            # If the schedule was canceled
            if self.canceled:
                # Cancel all appointmens of the original_schedule schedule range
                for appointment in appointments_in_original_schedule:
                    appointment.set_canceled_state()
                    print("Appointment: " + str(appointment) + ' was CANCELED!')

            # If there is a change in the date
            elif self.schedule_date != original_schedule.schedule_date:
                # Cancel all appointmens of the original_schedule schedule range
                for appointment in appointments_in_original_schedule:
                    appointment.set_canceled_state()
                    print("Appointment: " + str(appointment) + ' was CANCELED!')

            # If there is a change in the time range
            elif self.start_time != original_schedule.start_time or self.end_time != original_schedule.end_time:
                start = datetime.datetime.combine(self.schedule_date, self.start_time)
                end = datetime.datetime.combine(self.schedule_date, self.end_time)
                appointments_in_new_schedule = Appointment.objects.filter(
                    doctor=self.doctor,
                    appointment_date__range=(start, end)
                )

                set1 = set(appointments_in_original_schedule)
                set2 = set(appointments_in_new_schedule)

                missing_appointments = list(sorted(set1 - set2))

                print('missing:', missing_appointments)
                for missing_appointment in missing_appointments:
                    missing_appointment.set_canceled_state()
                    print("Appointment: " + str(missing_appointment) + ' was CANCELED!')

        super(Schedule, self).save(*args, **kwargs)


auditlog.register(Schedule)


# APPOINTMENT
class Appointment(SoftDeleteObject, TimeStampModel):
    patient = models.ForeignKey(
        to=Patient, on_delete=models.PROTECT,
        null=False, blank=False,
        verbose_name=_('Patient'),
        related_name='appointments',
    )
    contact_number = models.CharField(
        verbose_name=_('Contact Number'),
        null=False, blank=False,
        max_length=15
    )
    contact_email = models.EmailField(
        verbose_name=_('Contact Email'),
        null=True, blank=True
    )
    medical_study = models.ForeignKey(
        to=MedicalStudy, on_delete=models.PROTECT,
        null=False, blank=False,
        verbose_name=_('Medical Study'),
        related_name='appointments',
    )
    medical_equipment = models.ForeignKey(
        to=MedicalEquipment, on_delete=models.PROTECT,
        verbose_name=_('Medical Equipment'),
        null=True, blank=True,
        related_name='appointments',
    )
    appointment_date_start = models.DateTimeField(
        verbose_name=_('Appointment date start'),
        null=False, blank=False
    )
    appointment_date_end = models.DateTimeField(
        verbose_name=_('Appointment date end'),
        null=False, blank=False
    )

    doctor = models.ForeignKey(
        to=Doctor, on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name=_('Doctor'),
        related_name='appointments'
    )
    appointment_state = models.ForeignKey(
        to=AppointmentState, on_delete=models.PROTECT,
        null=False, blank=False,
        verbose_name=_('Appointment State'),
        related_name='appointments'
    )
    insurance_plan = models.ForeignKey(
        to=InsurancePlan, on_delete=models.PROTECT,
        null=True, blank=True,
        verbose_name=_('Insurance Plan'),
        related_name='appointments'
    )
    estimated_cost = models.FloatField(
        verbose_name=_('Estimated Cost'),
        null=True, blank=True,
        default=0
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='appointments'
    )
    treating_doctor = models.ForeignKey(
        to=TreatingDoctor, on_delete=models.PROTECT,
        verbose_name=_('Treating Doctor'),
        null=True, blank=True,
        related_name='appointments'
    )
    observations = models.TextField(
        verbose_name=_('Observations'),
        null=True, blank=True
    )

    class Meta:
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')

    def __str__(self):
        return 'ID:' + str(self.id) + ' - ' + str(self.patient) + ' - ' + str(self.medical_study) + ' - ' + self.appointment_date_start.strftime("%d/%m/%Y %H:%M") + ' - ' + self.appointment_date_end.strftime("%d/%m/%Y %H:%M")

    def set_canceled_state(self):
        canceled_state = AppointmentState.objects.get(state_code=AppointmentState.CANCELED_STATE)
        self.appointment_state = canceled_state
        self.save()


auditlog.register(Appointment)


class AppointmentStateUserLog(SoftDeleteObject, TimeStampModel):
    appointment = models.ForeignKey(
        to=Appointment, on_delete=models.PROTECT,
        verbose_name=_('Appointment'),
        related_name='appointment_states_user_logs',
        null=False, blank=False
    )
    appointment_state = models.ForeignKey(
        to=AppointmentState, on_delete=models.PROTECT,
        verbose_name=_('Appointment State'),
        related_name='appointment_states_user_logs',
        null=False, blank=False
    )
    user = models.ForeignKey(
        to=User, on_delete=models.PROTECT,
        verbose_name=_('User'),
        related_name='appointment_states_user_logs',
        null=False, blank=False
    )
    state_log_datetime = models.DateTimeField(
        verbose_name=_('State log datetime'),
        null=False, blank=False,
        auto_now=True
    )

    class Meta:
        verbose_name = _('Appointment State User Log')
        verbose_name_plural = _('Appointments States User Logs')
        # unique_together = ('appointment', 'appointment_state')

    def __str__(self):
        return str(self.appointment) + ' - ' + str(self.appointment_state) + ' - ' + str(self.user) + ' - ' + self.state_log_datetime.strftime("%d/%m/%Y %H:%M")


auditlog.register(AppointmentStateUserLog)


# ########################## APPOINTMENT DOCUMENT TYPE
class AppointmentDocumentType(SoftDeleteObject, TimeStampModel):
    name = models.CharField(verbose_name=_('Name'), max_length=250)

    class Meta:
        verbose_name = _('Appointment Document Type')
        verbose_name_plural = _('Appointment Document Types')

    def __str__(self):
        return str(self.name)


auditlog.register(AppointmentDocumentType)


# ############################ APPOINTMENT DOCUMENT
class AppointmentDocument(SoftDeleteObject, TimeStampModel):
    appointment = models.ForeignKey(
        to=Appointment, on_delete=models.PROTECT,
        verbose_name=_('Appointment'),
        null=False, blank=False,
        related_name='appointment_documents'
    )
    document_type = models.ForeignKey(
        to=AppointmentDocumentType, on_delete=models.PROTECT,
        verbose_name=_('Document Type'),
        null=False, blank=False,
        related_name='appointment_documents'
    )
    file = models.FileField(
        verbose_name=_('File'),
        upload_to=appointment_document_storage_path,
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('Appointment Document')
        verbose_name_plural = _('Appointment Documents')

    def __str__(self):
        return 'Document ' + str(self.id) + " - " + str(self.appointment)

    def get_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()


auditlog.register(AppointmentDocument)

