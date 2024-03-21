from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from consultation.models import Consultation, MedicalSupplyUsed, ConsultationFileType, ConsultationFile, \
    ConsultationSheet, ConsultationSheetDocument, ConsultationSheetDocumentType, ConsultationState, \
    ConsultationStateUserLog, ConsultationEntrySheet, ConsultationReport, DoctorReportTemplate


# Register your models here.

# Medical Supply Used Inline
class MedicalSupplyUsedInlineAdmin(admin.TabularInline):
    model = MedicalSupplyUsed


# Consultation Sheet Document Inline
class ConsultationSheetDocumentInlineAdmin(admin.TabularInline):
    model = ConsultationSheetDocument


# Consultation File Inline
class ConsultationTextFileInlineAdmin(admin.TabularInline):
    model = ConsultationFile


# ############################### CONSULTATION
class ConsultationResource(resources.ModelResource):

    class Meta:
        model = Consultation


class ConsultationAdmin(ImportExportModelAdmin):
    resource_class = ConsultationResource
    search_fields = ['id', 'patient__name', 'doctor__name', 'treating_doctor__name',
                     'medical_study__name', 'technician__name', 'technician__last_name', 'medical_equipment__name', 'patient_insurance_plan__name']
    list_filter = ['consultation_date', 'created_at', 'updated_at']

    list_display = (
        'id',
        'patient',
        'doctor',
        'treating_doctor',
        'consultation_date',
        'medical_study',
        'technician',
        'medical_equipment',
        'notes',
        'created_at',
        'updated_at'
    )

    inlines = [
        ConsultationTextFileInlineAdmin,
    ]


admin.site.register(Consultation, ConsultationAdmin)


# ############################### CONSULTATION Report
class ConsultationReportResource(resources.ModelResource):

    class Meta:
        model = ConsultationReport


class ConsultationReportAdmin(ImportExportModelAdmin):
    resource_class = ConsultationReportResource
    search_fields = ['id', 'patient__name', 'patient__last_name', 'doctor__name', 'doctor__last_name',
                     'patient_insurance_plan__name']
    list_filter = ['report_date', 'created_at', 'updated_at']

    list_display = (
        'id',
        'patient',
        'doctor',
        'report_date',
        'report',
        'created_at',
        'updated_at'
    )


admin.site.register(ConsultationReport, ConsultationReportAdmin)


# ############################### MEDICAL SUPPLY USED
class MedicalSupplyUsedResource(resources.ModelResource):

    class Meta:
        model = MedicalSupplyUsed


class MedicalSupplyUsedAdmin(ImportExportModelAdmin):
    resource_class = MedicalSupplyUsedResource
    search_fields = ['id', 'medical_supply__name']
    list_filter = ['currency', 'created_at', 'updated_at']

    list_display = (
        'id',
        'consultation_sheet',
        'medical_supply',
        'quantity',
        'price',
        'total_price',
        'cover_type',
        'insurance_agreement_coverage_percent',
        'insurance_agreement_coverage_amount',
        'ammount_to_pay_insurance',
        'ammount_to_pay_patient',
        'currency',
        'created_at',
        'updated_at'
    )


admin.site.register(MedicalSupplyUsed, MedicalSupplyUsedAdmin)


# ################################ CONSULTATION FILE TYPE
class ConsultationFileTypeResource(resources.ModelResource):

    class Meta:
        model = ConsultationFileType


class ConsultationFileTypeAdmin(ImportExportModelAdmin):
    resource_class = ConsultationFileTypeResource
    search_fields = ['id', 'name', 'extension']
    list_filter = ['type', 'created_at', 'updated_at']

    list_display = (
        'id',
        'name',
        'extension',
        'type',
        'created_at',
        'updated_at'
    )


admin.site.register(ConsultationFileType, ConsultationFileTypeAdmin)


# ################################## CONSULTATION FILE
class ConsultationFileResource(resources.ModelResource):

    class Meta:
        model = ConsultationFile


class ConsultationFileAdmin(ImportExportModelAdmin):
    resource_class = ConsultationFileResource
    search_fields = ['id', 'file_name']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'id',
        'file_name',
        'consultation',
        'consultation_file_type',
        'file',
        'created_at',
        'updated_at'
    )


# admin.site.register(ConsultationTextFile, ConsultationTextFileAdmin)


# ############################### CONSULTATION ENTRY SHEET
class ConsultationEntrySheetResource(resources.ModelResource):

    class Meta:
        model = ConsultationEntrySheet


class ConsultationEntrySheetAdmin(ImportExportModelAdmin):
    resource_class = ConsultationEntrySheetResource
    search_fields = ['id', 'patient__name', 'patient__last_name',
                     ]
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'id',
        'patient',
        'total_amount',
        'total_amount_to_pay_insurance',
        'total_amount_to_pay_patient',
        'total_amount_paid_by_patient',
        'patient_balance',
        'created_at',
        'updated_at'
    )


admin.site.register(ConsultationEntrySheet, ConsultationEntrySheetAdmin)


# ############################### CONSULTATION SHEET
class ConsultationSheetResource(resources.ModelResource):

    class Meta:
        model = ConsultationSheet


class ConsultationSheetAdmin(ImportExportModelAdmin):
    resource_class = ConsultationSheetResource
    search_fields = ['id', 'patient__name',  'patient__last_name', 'treating_doctor__name', 'treating_doctor__last_name',
                     'doctor__name',  'doctor__last_name',
                     'payment_method__name', 'payment_reference',
                     'medical_study__name', 'patient_insurance_plan__name',
                     ]
    list_filter = ['consultation_state', 'payment_method', 'patient_insurance_plan', 'created_at', 'updated_at']

    list_display = (
        'id',
        'patient',
        'patient_insurance_plan',
        'medical_study',
        'study_cover_type',
        'insurance_agreement_coverage_percent',
        'insurance_agreement_coverage_amount',
        'medical_equipment',
        'doctor',
        'technician',
        'payment_method',
        'medical_study_ammount',
        'medical_study_ammount_to_pay_insurance',
        'medical_study_ammount_to_pay_patient',
        'medical_supplies_ammount',
        'medical_supplies_ammount_to_pay_insurance',
        'medical_supplies_ammount_to_pay_patient',
        'total_amount',
        'total_ammount_to_pay_insurance',
        'total_ammount_to_pay_patient',
        'amount_paid',
        'currency',
        'payment_reference',
        'treating_doctor',
        'reporting_doctor',
        'appointment',
        'consultation_state',
        'created_at',
        'updated_at'
    )

    inlines = [
        ConsultationSheetDocumentInlineAdmin,
        MedicalSupplyUsedInlineAdmin,
    ]


admin.site.register(ConsultationSheet, ConsultationSheetAdmin)


# ############################### CONSULTATION SHEET DOCUMENT TYPE
class ConsultationSheetDocumentTypeResource(resources.ModelResource):

    class Meta:
        model = ConsultationSheetDocumentType


class ConsultationSheetDocumentTypeAdmin(ImportExportModelAdmin):
    resource_class = ConsultationSheetDocumentTypeResource
    search_fields = ['id', 'name']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'id',
        'name',
        'created_at',
        'updated_at'
    )


admin.site.register(ConsultationSheetDocumentType, ConsultationSheetDocumentTypeAdmin)


# ############################### CONSULTATION STATE
class ConsultationStateResource(resources.ModelResource):

    class Meta:
        model = ConsultationState


class ConsultationStateAdmin(ImportExportModelAdmin):
    resource_class = ConsultationStateResource
    search_fields = ['id', 'name']
    list_filter = ['state_code', 'created_at', 'updated_at']

    list_display = (
        'id',
        'name',
        'state_code',
        'created_at',
        'updated_at'
    )


admin.site.register(ConsultationState, ConsultationStateAdmin)


# ############################### CONSULTATION STATE USER LOG
class ConsultationStateUserLogResource(resources.ModelResource):

    class Meta:
        model = ConsultationStateUserLog


class ConsultationStateUserLogAdmin(ImportExportModelAdmin):
    resource_class = ConsultationStateResource
    search_fields = ['id', 'consultation_sheet__patient__name', 'consultation_sheet__patient__last_name', 'consultation_state__name', 'user__username']
    list_filter = ['consultation_state', 'created_at', 'updated_at']

    list_display = (
        'id',
        'consultation_sheet',
        'consultation_state',
        'user',
        'state_log_datetime',
        'created_at',
        'updated_at'
    )


admin.site.register(ConsultationStateUserLog, ConsultationStateUserLogAdmin)


# ############################### Doctor Report Template
class DoctorReportTemplateResource(resources.ModelResource):

    class Meta:
        model = DoctorReportTemplate


class DoctorReportTemplateAdmin(ImportExportModelAdmin):
    resource_class = DoctorReportTemplateResource
    search_fields = ['id', 'doctor__name', 'doctor__last_name', 'medical_study__name']
    list_filter = ['medical_study__name', 'digital_signature', 'created_at', 'updated_at']

    list_display = (
        'id',
        'doctor',
        'medical_study',
        'digital_signature',
        'created_at',
        'updated_at'
    )


admin.site.register(DoctorReportTemplate, DoctorReportTemplateAdmin)
