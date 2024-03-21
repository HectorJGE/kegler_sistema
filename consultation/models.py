import os

from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from softdelete.models import SoftDeleteObject
from django.utils.translation import ugettext_lazy as _
from auditlog.registry import auditlog
from base.models import Currency, TimeStampModel
from clinic.models import InsurancePlan, MedicalEquipment, Technician, MedicalStudy, TreatingDoctor, Doctor, Patient, MedicalStudyInsuranceAgreement, MedicalSupplyInsuranceAgreement
from invoicing.models import PaymentMethod, InvoiceHeader, CreditNoteHeader
from scheduling.models import Appointment
from stock.models import Product


# Consultation Sheet Documents Upload to
def consultation_sheet_document_storage_path(instance, filename):
    return 'consultation_sheets/{0}/documents/{1}'.format(str(instance.consultation_sheet.id), filename)


# Consultation Report Audio Upload to
def consultation_report_audio_storage_path(instance, filename):
    return 'consultation_reports/{0}/audios/{1}'.format(str(instance.id), filename)


# ConsultationFile Upload to
def consultation_file_storage_path(instance, filename):
    return 'consultation/patient_files/{0}/{1}'.format(str(instance.consultation.patient.document_number), filename)


# CONSULTATION STATE
class ConsultationState(SoftDeleteObject, TimeStampModel):
    FILED_STATE = 0
    PERFORMED_STATE = 1
    ASSIGNED_STATE = 2
    REPORTED_STATE = 3
    PREPARED_STATE = 4
    DELIVERED_STATE = 5

    RECORDED_STATE = 6
    COPIED_STATE = 7
    FINISHED_STATE = 8

    STATES_CODES = (
        (FILED_STATE, _('Filed')),
        (PERFORMED_STATE, _('Performed')),
        (ASSIGNED_STATE, _('Assigned')),

        (RECORDED_STATE, _('Recorded')),
        (COPIED_STATE, _('Copied')),
        (FINISHED_STATE, _('Finished')),

        (REPORTED_STATE, _('Reported')),
        (PREPARED_STATE, _('Prepared')),
        (DELIVERED_STATE, _('Delivered')),
    )
    name = models.CharField(max_length=50, verbose_name=_('Name'), null=False, blank=False)
    state_code = models.IntegerField(
        verbose_name=_('State code'),
        choices=STATES_CODES,
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('Consultation State')
        verbose_name_plural = _('Consultation States')

    def __str__(self):
        return self.name


auditlog.register(ConsultationState)


# #################################  Consultation Entry Sheet
class ConsultationEntrySheet(SoftDeleteObject, TimeStampModel):
    consultation_entry_sheet_date = models.DateTimeField(
        verbose_name=_('Consultation Entry Sheet Date'),
        null=False, blank=False,
        default=timezone.now
    )
    invoice = models.ForeignKey(
        to=InvoiceHeader, on_delete=models.PROTECT,
        verbose_name=_('Invoice'),
        null=True, blank=True,
        related_name='consultation_entry_sheets'
    )
    insurance_invoice = models.ForeignKey(
        to=InvoiceHeader, on_delete=models.PROTECT,
        verbose_name=_('Insurance Invoice'),
        null=True, blank=True,
        related_name='insurance_invoice_consultation_entry_sheets'
    )
    patient = models.ForeignKey(
        to=Patient, on_delete=models.PROTECT,
        verbose_name=_('Patient'),
        null=False, blank=False,
        related_name='consultation_entry_sheets'
    )
    total_amount = models.FloatField(
        verbose_name=_('Total amount'),
        null=False, blank=False,
        default=0
    )
    total_amount_to_pay_insurance = models.FloatField(
        verbose_name=_('Total amount to pay insurance'),
        null=False, blank=False,
        default=0
    )
    total_amount_to_pay_patient = models.FloatField(
        verbose_name=_('Total amount to pay patient'),
        null=False, blank=False,
        default=0
    )
    total_amount_paid_by_patient = models.FloatField(
        verbose_name=_('Total amount Paid by Patient'),
        null=False, blank=False,
        default=0
    )
    patient_balance = models.FloatField(
        verbose_name=_('Patient Balance'),
        null=False, blank=False,
        default=0
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='consultation_entrey_sheets'
    )

    class Meta:
        verbose_name = _('Consultation Entry Sheet')
        verbose_name_plural = _('Consultation Entry Sheets')

    def __str__(self):
        return str(self.patient) + ' - ' + self.consultation_entry_sheet_date.strftime("%A") + " " + self.consultation_entry_sheet_date.strftime("%d/%m/%Y %H:%M")


auditlog.register(ConsultationEntrySheet)


# ############################################ CONSULTATION SHEET
class ConsultationSheet(SoftDeleteObject, TimeStampModel):
    consultation_date = models.DateTimeField(
        verbose_name=_('Consultation Date'),
        null=False, blank=False,

    )
    patient = models.ForeignKey(
        to=Patient, on_delete=models.PROTECT,
        verbose_name=_('Patient'),
        null=False, blank=False,
        related_name='consultation_sheets'
    )
    patient_insurance_plan = models.ForeignKey(
        to=InsurancePlan, on_delete=models.PROTECT,
        verbose_name=_('Patient Insurance Plan'),
        null=True, blank=True,
        related_name='consultation_sheets'
    )
    medical_study = models.ForeignKey(
        to=MedicalStudy, on_delete=models.PROTECT,
        verbose_name=_('Medical Study'),
        related_name='consultation_sheets',
        null=False, blank=False,
    )
    COVER_TYPES = (
        (0, _('Percentage')),
        (1, _('Amount')),
    )
    study_cover_type = models.IntegerField(
        verbose_name=_('Study Cover Type'),
        null=False, blank=False,
        default=0,
        choices=COVER_TYPES
    )
    insurance_agreement_coverage_percent = models.FloatField(
        verbose_name=_('Insurance Agreement Coverage Percent'),
        default=0
    )
    insurance_agreement_coverage_amount = models.FloatField(
        verbose_name=_('Insurance Agreement Coverage Amount'),
        default=0
    )
    medical_equipment = models.ForeignKey(
        to=MedicalEquipment, on_delete=models.PROTECT,
        verbose_name=_('Medical Equipment Used'),
        related_name='consultation_sheets',
        null=True, blank=True,
    )
    doctor = models.ForeignKey(
        to=Doctor, on_delete=models.PROTECT,
        verbose_name=_('Doctor'),
        related_name='doctor_consultation_sheets',
        null=True, blank=True,
    )
    technician = models.ForeignKey(
        to=Technician, on_delete=models.PROTECT,
        verbose_name=_('Technician'),
        related_name='consultation_sheets',
        null=True, blank=True,
    )
    payment_method = models.ForeignKey(
        to=PaymentMethod, on_delete=models.PROTECT,
        verbose_name=_('Payment Method'),
        related_name='consultation_sheets',
        null=True, blank=True,
    )
    payment_reference = models.CharField(
        max_length=100,
        verbose_name=_('Payment Reference'),
        null=True, blank=True
    )
    treating_doctor = models.ForeignKey(
        to=TreatingDoctor, on_delete=models.PROTECT,
        verbose_name=_('Treating Doctor'),
        null=True, blank=True,
        related_name='treating_doctor_consultation_sheets'
    )
    reporting_doctor = models.ForeignKey(
        to=Doctor, on_delete=models.PROTECT,
        verbose_name=_('Reporting Doctor'),
        related_name='reporting_doctor_consultation_sheets',
        null=True, blank=True,
    )
    appointment = models.ForeignKey(
        to=Appointment, on_delete=models.PROTECT,
        verbose_name=_('Appointment'),
        null=True, blank=True,
        related_name='consultation_sheets',
        default=None
    )
    medical_study_ammount = models.FloatField(
        verbose_name=_('Medical Study Ammount'),
        null=False, blank=False,
        default=0
    )
    medical_study_ammount_to_pay_insurance = models.FloatField(
        verbose_name=_('Medical Study Ammount to pay (Insurance)'),
        null=False, blank=False,
        default=0
    )
    medical_study_ammount_to_pay_patient = models.FloatField(
        verbose_name=_('Medical Study Ammount to pay (Patient)'),
        null=False, blank=False,
        default=0
    )
    medical_supplies_ammount = models.FloatField(
        verbose_name=_('Medical Supplies Ammount'),
        null=False, blank=False,
        default=0
    )
    medical_supplies_ammount_to_pay_insurance = models.FloatField(
        verbose_name=_('Medical Supplies Ammount to pay (Insurance)'),
        null=False, blank=False,
        default=0
    )
    medical_supplies_ammount_to_pay_patient = models.FloatField(
        verbose_name=_('Medical Supplies Ammount to pay (Patient)'),
        null=False, blank=False,
        default=0
    )
    discount = models.FloatField(
        verbose_name=_('Discount'),
        null=True, blank=True,
        default=0
    )
    total_amount = models.FloatField(
        verbose_name=_('Total Amount'),
        null=False, blank=False,
        default=0
    )
    total_ammount_to_pay_insurance = models.FloatField(
        verbose_name=_('Total Amount to pay Insurance'),
        null=False, blank=False,
        default=0
    )
    total_ammount_to_pay_patient = models.FloatField(
        verbose_name=_('Total Amount to pay Patient'),
        null=False, blank=False,
        default=0
    )
    total_ammount_to_pay_patient_with_discount = models.FloatField(
        verbose_name=_('Total Amount to pay Patient with discount'),
        null=False, blank=False,
        default=0
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='consultation_sheets'
    )
    consultation_state = models.ForeignKey(
        to=ConsultationState, on_delete=models.PROTECT,
        verbose_name=_('Consultation State'),
        related_name='consultation_sheets',
        null=False, blank=False,
    )
    received_by = models.CharField(
        verbose_name=_('Received by (Name - and Document Number)'),
        max_length=100,
        null=True, blank=True
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
    internal_results_delivery_date = models.DateTimeField(
        verbose_name=_('Internal Results Delivery Date'),
        null=True, blank=True,
    )
    patient_results_delivery_date = models.DateTimeField(
        verbose_name=_('Patient Results Delivery Date'),
        null=True, blank=True,
    )
    consultation_entry_sheet = models.ForeignKey(
        to=ConsultationEntrySheet, on_delete=models.PROTECT,
        verbose_name=_('Consultation Entry Sheet'),
        related_name='consultation_sheets',
        null=True, blank=True,
        default=None
    )
    observations = models.TextField(
        verbose_name=_('Observations'),
        null=True, blank=True
    )
    amount_paid = models.FloatField(
        verbose_name=_('Amount Paid'),
        null=True, blank=True,
        default=0
    )
    patient_balance = models.FloatField(
        verbose_name=_('Patient Balance'),
        null=False, blank=False,
        default=0
    )

    class Meta:
        verbose_name = _('Consultation Sheet')
        verbose_name_plural = _('Consultation Sheets')

    def __str__(self):
        return str(self.patient) + ' - ' + str(self.medical_study) + ' - ' + self.consultation_date.strftime("%d/%m/%Y %H:%M")


auditlog.register(ConsultationSheet)


# CONSULTATION REPORT
class ConsultationReport(SoftDeleteObject, TimeStampModel):
    report_title = models.CharField(
        null=True, blank=False,
        verbose_name=_('Report Title'),
        max_length=200
    )
    patient = models.ForeignKey(
        to=Patient, on_delete=models.PROTECT,
        verbose_name=_('Patient'),
        null=True, blank=True,
        related_name='consultation_reports'
    )
    doctor = models.ForeignKey(
        to=Doctor, on_delete=models.PROTECT,
        verbose_name=_('Doctor'),
        related_name='consultation_reports',
        null=True, blank=True,
    )
    report_date = models.DateTimeField(
        verbose_name=_('Report Date'),
        null=False, blank=False,
        default=timezone.now
    )
    add_digital_signature = models.BooleanField(
        verbose_name=_('Add Digital Signature'),
        null=False, blank=True,
        default=False
    )
    report = RichTextField(
        verbose_name=_('Report'),
        null=True, blank=True
    )
    audio_report = models.FileField(
        verbose_name=_('Audio Report'),
        null=True, blank=True,
        default=None,
        upload_to=consultation_report_audio_storage_path,
    )
    finished = models.BooleanField(
        verbose_name=_('Mark as Finished'),
        default=False
    )

    class Meta:
        verbose_name = _('Consultation Report')
        verbose_name_plural = _('Consultations Reports')

    def __str__(self):
        return str(self.patient) + " - " + str(self.doctor)


auditlog.register(ConsultationReport)


# CONSULTATION
class Consultation(SoftDeleteObject, TimeStampModel):
    consultation_sheet = models.OneToOneField(
        to=ConsultationSheet,
        on_delete=models.PROTECT,
        verbose_name=_('Consultation Sheet'),
        null=False, blank=False,
        related_name='consults'
    )
    patient = models.ForeignKey(
        to=Patient, on_delete=models.PROTECT,
        verbose_name=_('Patient'),
        null=False, blank=False,
        related_name='consults'
    )
    doctor = models.ForeignKey(
        to=Doctor, on_delete=models.PROTECT,
        verbose_name=_('Doctor'),
        related_name='consults',
        null=True, blank=True,
    )
    treating_doctor = models.ForeignKey(
        to=TreatingDoctor, on_delete=models.PROTECT,
        verbose_name=_('Treating Doctor'),
        null=True, blank=True,
        related_name='consults'
    )
    consultation_date = models.DateTimeField(
        verbose_name=_('Consultation Date'),
        null=False, blank=False,
        default=timezone.now
    )
    medical_study = models.ForeignKey(
        to=MedicalStudy, on_delete=models.PROTECT,
        verbose_name=_('Medical Study'),
        related_name='consults',
        null=False, blank=False,
    )
    technician = models.ForeignKey(
        to=Technician, on_delete=models.PROTECT,
        verbose_name=_('Technician'),
        related_name='consults',
        null=True, blank=True,
    )
    medical_equipment = models.ForeignKey(
        to=MedicalEquipment, on_delete=models.PROTECT,
        verbose_name=_('Medical Equipment'),
        null=True, blank=True,
        related_name='consults'
    )
    notes = RichTextField(
        verbose_name=_('Notes')
    )
    consultation_report = models.ForeignKey(
        to=ConsultationReport, on_delete=models.PROTECT,
        verbose_name=_('Consultation Report'),
        null=True, blank=True,
        related_name='consults'
    )

    class Meta:
        verbose_name = _('Consultation')
        verbose_name_plural = _('Consultations')

    def __str__(self):
        if self.doctor:
            return str(self.patient) + " - " + str(self.medical_study) + " - " + str(self.doctor)
        else:
            return str(self.patient) + " - " + str(self.medical_study) + " - " + str(self.medical_equipment)


auditlog.register(Consultation)


# ########################## CONSULTATION SHEET DOCUMENT TYPE
class ConsultationSheetDocumentType(SoftDeleteObject, TimeStampModel):
    name = models.CharField(verbose_name=_('Name'), max_length=250)

    class Meta:
        verbose_name = _('Consultation Sheet Document Type')
        verbose_name_plural = _('Consultation Sheet Document Types')

    def __str__(self):
        return str(self.name)


auditlog.register(ConsultationSheetDocumentType)


# ############################ CONSULTATION SHEET DOCUMENT
class ConsultationSheetDocument(SoftDeleteObject, TimeStampModel):
    consultation_sheet = models.ForeignKey(
        to=ConsultationSheet, on_delete=models.PROTECT,
        verbose_name=_('Consultation'),
        null=False, blank=False,
        related_name='consultation_sheet_documents'
    )
    document_type = models.ForeignKey(
        to=ConsultationSheetDocumentType, on_delete=models.PROTECT,
        verbose_name=_('Document Type'),
        null=False, blank=False,
        related_name='consultation_sheet_documents'
    )
    file = models.FileField(
        verbose_name=_('File'),
        upload_to=consultation_sheet_document_storage_path,
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('Consultation Sheet Document')
        verbose_name_plural = _('Consultation Sheet Documents')

    def __str__(self):
        return 'Document ' + str(self.id) + " - " + str(self.consultation_sheet)

    def get_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()


auditlog.register(ConsultationSheetDocument)


# MEDICAL SUPPLY USED CONSULTATION SHEET
class MedicalSupplyUsed(SoftDeleteObject, TimeStampModel):
    consultation_sheet = models.ForeignKey(
        to=ConsultationSheet, on_delete=models.PROTECT,
        verbose_name=_('Consultation Sheet'),
        null=False, blank=False,
        related_name='medical_supplies_used'
    )
    medical_supply = models.ForeignKey(
        to=Product, on_delete=models.PROTECT,
        verbose_name=_('Medical Supply'),
        null=False, blank=False,
        related_name='medical_supplies_used'
    )
    quantity = models.FloatField(
        verbose_name=_('Quantity'),
        null=False, blank=False
    )
    price = models.FloatField(
        verbose_name=_('Price'),
        null=False, blank=False,
        default=0
    )
    total_price = models.FloatField(
        verbose_name=_('Total'),
        null=False, blank=False,
        default=0
    )
    COVER_TYPES = (
        (0, _('Percentage')),
        (1, _('Amount')),
    )
    cover_type = models.IntegerField(
        verbose_name=_('Cover Type'),
        null=False, blank=False,
        default=0,
        choices=COVER_TYPES
    )
    insurance_agreement_coverage_percent = models.FloatField(
        verbose_name=_('Insurance Agreement Coverage Percent'),
        default=0
    )
    insurance_agreement_coverage_amount = models.FloatField(
        verbose_name=_('Insurance Agreement Coverage Amount'),
        default=0
    )
    ammount_to_pay_insurance = models.FloatField(
        verbose_name=_('Ammount to Pay Insurance'),
        default=0
    )
    ammount_to_pay_patient = models.FloatField(
        verbose_name=_('Ammount to Pay Patient'),
        default=0
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='medical_supplies_used'
    )

    class Meta:
        verbose_name = _('Medical Supply Used')
        verbose_name_plural = _('Medical Supplies Used')

    def __str__(self):
        return str(self.consultation_sheet) + ' - ' + str(self.medical_supply)


auditlog.register(MedicalSupplyUsed)


# CONSULTATION FILE TYPE
class ConsultationFileType(SoftDeleteObject, TimeStampModel):
    IMAGE_TYPE = 0
    VIDEO_TYPE = 1
    SOUND_TYPE = 2
    TEXT_TYPE = 3

    FYLE_TYPES = (
        (0, _('Image')),
        (1, _('Sound')),
        (2, _('Video')),
        (3, _('Text')),
    )
    name = models.CharField(max_length=100, verbose_name=_('Name'), null=False, blank=False)
    extension = models.CharField(verbose_name=_('Extension'), max_length=10)
    type = models.IntegerField(verbose_name=_('Types'), choices=FYLE_TYPES, null=False, blank=False)

    class Meta:
        verbose_name = _('Consultation File Type')
        verbose_name_plural = _('Consultation File Types')

    def __str__(self):
        return self.name


auditlog.register(ConsultationFileType)


# CONSULTATION FILES
class ConsultationFile(SoftDeleteObject, TimeStampModel):
    file_name = models.CharField(verbose_name=_('File Name'), max_length=250)
    consultation = models.ForeignKey(
        to=Consultation, on_delete=models.CASCADE,
        verbose_name=_('Consultation'),
        null=False, blank=False,
        related_name='consultation_files'
    )
    consultation_file_type = models.ForeignKey(
        to=ConsultationFileType, on_delete=models.PROTECT,
        verbose_name=_('File type'),
        null=False, blank=False,
        related_name='consultation_files'
    )
    file = models.FileField(
        verbose_name=_('File'),
        upload_to=consultation_file_storage_path,
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('Consultation File')
        verbose_name_plural = _('Consultation Text Files')

    def __str__(self):
        return str(self.consultation) + ' - ' + self.file_name


auditlog.register(ConsultationFile)


class ConsultationStateUserLog(SoftDeleteObject, TimeStampModel):
    consultation_sheet = models.ForeignKey(
        to=ConsultationSheet, on_delete=models.PROTECT,
        verbose_name=_('Consultation Sheet'),
        related_name='consultation_states_user_logs',
        null=False, blank=False
    )
    consultation_state = models.ForeignKey(
        to=ConsultationState, on_delete=models.PROTECT,
        verbose_name=_('Consultation State'),
        related_name='consultation_states_user_logs',
        null=False, blank=False
    )
    user = models.ForeignKey(
        to=User, on_delete=models.PROTECT,
        verbose_name=_('User'),
        related_name='consultation_states_user_logs',
        null=False, blank=False
    )
    state_log_datetime = models.DateTimeField(
        verbose_name=_('State log datetime'),
        null=False, blank=False,
        auto_now=True
    )

    class Meta:
        verbose_name = _('Consultation State User Log')
        verbose_name_plural = _('Consultations States User Logs')
        # unique_together = ('consultation_sheet', 'consultation_state')

    def __str__(self):
        return str(self.consultation_sheet) + ' - ' + str(self.consultation_state) + ' - ' + str(self.user) + ' - ' + self.state_log_datetime.strftime("%d/%m/%Y %H:%M")


auditlog.register(ConsultationStateUserLog)


class DoctorReportTemplate(SoftDeleteObject, TimeStampModel):
    doctor = models.ForeignKey(
        to=Doctor, on_delete=models.PROTECT,
        verbose_name=_('Doctor'),
        related_name='doctor_reports_templates',
        null=False, blank=False
    )
    medical_study = models.ForeignKey(
        to=MedicalStudy, on_delete=models.PROTECT,
        verbose_name=_('Medical Study')
    )
    template_text = RichTextField(
        verbose_name=_('Template Text'),
        null=False, blank=False
    )
    digital_signature = models.BooleanField(
        verbose_name=_('Digital Signature'),
        null=True, blank=True,
        default=False
    )

    class Meta:
        verbose_name = _('Doctor Report Template')
        verbose_name_plural = _('Doctors Reports Templates')

    def __str__(self):
        return str(self.doctor) + ' - ' + str(self.medical_study)


auditlog.register(DoctorReportTemplate)

