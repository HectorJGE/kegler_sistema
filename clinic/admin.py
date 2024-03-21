from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import ugettext_lazy as _
from clinic.models import InsuranceCompany, InsurancePlan, Patient, DoctorSpecialization, Doctor, TreatingDoctor, TechnicianSpecialization, Technician, MedicalStudy, \
    MedicalEquipment, DoctorMedicalStudy, MedicalEquipmentType, InsurancePlanMedicalStudyFee, MedicalStudyType, MedicalSupplyInsuranceAgreement, Sector, InsurancePlanMedicalSupplyFee
from consultation.models import MedicalStudyInsuranceAgreement
from scheduling.admin import DefaultDoctorAppointmentScheduleInlineAdmin, ScheduleInlineAdmin


# Register your models here.

# Insurance Plan Inline
class InsurancePlanInlineAdmin(admin.TabularInline):
    model = InsurancePlan
    extra = 0


# Doctor Medical Study Inline
class DoctorMedicalStudyInlineAdmin(admin.TabularInline):
    model = DoctorMedicalStudy
    extra = 0


# ########################## INSURANCE COMPANY
class InsuranceCompanyResource(resources.ModelResource):

    class Meta:
        model = InsuranceCompany


class InsuranceCompanyAdmin(ImportExportModelAdmin):
    resource_class = InsuranceCompanyResource
    search_fields = ['id', 'name', 'tax_identification_number']
    list_filter = ['created_at', 'updated_at']

    list_display = ('id',
                    'name',
                    'tax_identification_number',
                    'email',
                    'address',
                    'phone_number',
                    'created_at',
                    'updated_at'
                    )
    inlines = [
        InsurancePlanInlineAdmin,
    ]


admin.site.register(InsuranceCompany, InsuranceCompanyAdmin)


# ########################### INSURANCE PLAN
class InsurancePlanResource(resources.ModelResource):

    class Meta:
        model = InsurancePlan


class InsurancePlanAdmin(ImportExportModelAdmin):
    resource_class = InsurancePlanResource
    search_fields = ['id', 'name', 'insurance_company__name']
    list_filter = ['insurance_company', 'created_at', 'updated_at']

    list_display = ('id', 'name', 'insurance_company', 'created_at', 'updated_at')


admin.site.register(InsurancePlan, InsurancePlanAdmin)


# ################################### PATIENT
class PatientResource(resources.ModelResource):

    class Meta:
        model = Patient


class PatientAdmin(ImportExportModelAdmin):
    resource_class = PatientResource
    search_fields = ['id', 'name', 'last_name',
                     'birth_date', 'document_number',
                     'email', 'phone_number', 'address',
                     'insurance_plan__name', 'tax_identification_number']
    list_filter = ['insurance_plan', 'birth_date', 'created_at', 'updated_at']

    list_display = ('id', 'name', 'last_name',
                    'birth_date', 'document_number',
                    'email', 'phone_number', 'address',
                    'insurance_plan', 'tax_identification_number',
                    'created_at',
                    'updated_at'
                    )


admin.site.register(Patient, PatientAdmin)


# ################################## DOCTOR SPECIALIZATION
class DoctorSpecializationResource(resources.ModelResource):

    class Meta:
        model = DoctorSpecialization


class DoctorSpecializationAdmin(ImportExportModelAdmin):
    resource_class = DoctorSpecializationResource
    search_fields = ['id', 'name']
    list_filter = ['created_at', 'updated_at']

    list_display = ('id', 'name', 'created_at', 'updated_at')


admin.site.register(DoctorSpecialization, DoctorSpecializationAdmin)


# ##################################  DOCTOR
class DoctorResource(resources.ModelResource):

    class Meta:
        model = Doctor


class DoctorAdmin(ImportExportModelAdmin):
    resource_class = DoctorResource
    search_fields = ['id', 'name', 'last_name', 'document_number', 'tax_identification_number', 'email', 'phone_number', 'address', 'doctor_specializations__name', 'sectors__name']
    list_filter = ['birth_date', 'created_at', 'updated_at', 'doctor_specializations']

    list_display = ('id', 'name', 'last_name', 'especializaciones',
                    'birth_date', 'document_number', 'tax_identification_number',
                    'email', 'phone_number', 'address', 'sectores', 'user', 'digital_signature',
                    'created_at',
                    'updated_at'
                    )
    inlines = [
        # DoctorMedicalStudyInlineAdmin,
        DefaultDoctorAppointmentScheduleInlineAdmin,

    ]

    def especializaciones(self, obj):
        return "\n".join([s.name for s in obj.doctor_specializations.all()])

    def sectores(self, obj):
        return "\n".join([s.name for s in obj.sectors.all()])


admin.site.register(Doctor, DoctorAdmin)


# ################################### TREATING DOCTOR
class TreatingDoctorResource(resources.ModelResource):

    class Meta:
        model = TreatingDoctor


class TreatingDoctorAdmin(ImportExportModelAdmin):
    resource_class = TreatingDoctorResource
    search_fields = ['id', 'name', 'last_name', 'document_number', 'tax_identification_number',
                     'email', 'phone_number', 'address', 'doctor_specializations__name']
    list_filter = ['birth_date', 'created_at', 'updated_at', 'doctor_specializations']

    list_display = ('id', 'name', 'last_name', 'especializaciones',
                    'birth_date', 'document_number', 'tax_identification_number',
                    'email', 'phone_number', 'address',
                    'created_at',
                    'updated_at'
                    )

    def especializaciones(self, obj):
        return "\n".join([s.name for s in obj.doctor_specializations.all()])


admin.site.register(TreatingDoctor, TreatingDoctorAdmin)


# #################################### TECHNICIAN SPECIALIZATION
class TechnicianSpecializationResource(resources.ModelResource):

    class Meta:
        model = TechnicianSpecialization


class TechnicianSpecializationAdmin(admin.ModelAdmin):
    resource_class = TechnicianSpecializationResource
    search_fields = ['id', 'name']
    list_filter = ['created_at', 'updated_at']

    list_display = ('id', 'name', 'created_at', 'updated_at')


admin.site.register(TechnicianSpecialization, TechnicianSpecializationAdmin)


# ####################################### TECHNICIAN
class TechnicianResource(resources.ModelResource):

    class Meta:
        model = Technician


class TechnicianAdmin(ImportExportModelAdmin):
    resource_class = TechnicianResource
    search_fields = ['id', 'name', 'last_name',
                     'document_number', 'tax_identification_number', 'technician_specializations__name',
                     'email', 'phone_number', 'address']
    list_filter = ['birth_date', 'created_at', 'updated_at', 'technician_specializations']

    list_display = ('id', 'name', 'last_name', 'especializaciones', 'sectores',
                    'birth_date', 'document_number', 'tax_identification_number',
                    'email', 'phone_number', 'address',
                    'created_at',
                    'updated_at'
                    )

    def especializaciones(self, obj):
        return "\n".join([s.name for s in obj.technician_specializations.all()])

    def sectores(self, obj):
        return "\n".join([s.name for s in obj.sectors.all()])


admin.site.register(Technician, TechnicianAdmin)


# #################################### MEDICAL STUDY TYPE
class MedicalStudyTypeResource(resources.ModelResource):

    class Meta:
        model = MedicalStudyType


class MedicalStudyTypeAdmin(ImportExportModelAdmin):
    resource_class = MedicalStudyTypeResource
    search_fields = ['id', 'name']
    list_filter = ['created_at', 'updated_at']

    list_display = ('id', 'name', 'created_at', 'updated_at')


admin.site.register(MedicalStudyType, MedicalStudyTypeAdmin)


# #################################### Medical Study
class MedicalStudyResource(resources.ModelResource):

    class Meta:
        model = MedicalStudy


class MedicalStudyAdmin(ImportExportModelAdmin):
    resource_class = MedicalStudyResource
    search_fields = ['id', 'name', 'sector__name']
    list_filter = ['type', 'created_at', 'updated_at']

    list_display = ('id', 'name', 'type', 'duration_in_minutes', 'sector', 'price', 'currency',
                    'created_at',
                    'updated_at')


admin.site.register(MedicalStudy, MedicalStudyAdmin)


# ################################  Medical Equipment
class MedicalEquipmentResource(resources.ModelResource):

    class Meta:
        model = MedicalEquipment


class MedicalEquipmentAmin(ImportExportModelAdmin):
    resource_class = MedicalEquipmentResource
    search_fields = ['id', 'name', 'sector__name']
    list_filter = ['created_at', 'updated_at']

    list_display = ('id', 'name', 'tag_color', 'sector',
                    'created_at',
                    'updated_at')


admin.site.register(MedicalEquipment, MedicalEquipmentAmin)


# ############################### Doctor Medical Study
class DoctorMedicalStudyResource(resources.ModelResource):

    class Meta:
        model = DoctorMedicalStudy


class DoctorMedicalStudyAdmin(ImportExportModelAdmin):
    resource_class = DoctorMedicalStudyResource
    search_fields = ['id', 'doctor__name', 'medical_study__name']
    list_filter = ['doctor', 'medical_study', 'created_at', 'updated_at']

    list_display = ('id', 'doctor', 'medical_study',
                    'created_at',
                    'updated_at')


# admin.site.register(DoctorMedicalStudy, DoctorMedicalStudyAdmin)


# ################################# Medical Equipment Type
class MedicalEquipmentTypeResource(resources.ModelResource):

    class Meta:
        model = MedicalEquipmentType


class MedicalEquipmentTypeAdmin(ImportExportModelAdmin):
    resource_class = MedicalEquipmentTypeResource
    search_fields = ['id', 'name', 'equipment_type_code']
    list_filter = ['created_at', 'updated_at']

    list_display = ('id', 'name', 'equipment_type_code',
                    'created_at',
                    'updated_at')


# admin.site.register(MedicalEquipmentType, MedicalEquipmentTypeAdmin)


# ############################### Insurance Plan Medical Study Fee
class InsurancePlanMedicalStudyFeeResource(resources.ModelResource):

    class Meta:
        model = InsurancePlanMedicalStudyFee


class InsurancePlanMedicalStudyFeeAdmin(ImportExportModelAdmin):
    resource_class = InsurancePlanMedicalStudyFeeResource
    search_fields = ['id', 'insurance_plan__name', 'medical_study__name']
    list_filter = ['medical_study__sector', 'insurance_plan', 'medical_study', 'currency', 'created_at', 'updated_at']

    list_display = ('id', 'insurance_plan', 'medical_study', 'price', 'currency', 'created_at', 'updated_at')


admin.site.register(InsurancePlanMedicalStudyFee, InsurancePlanMedicalStudyFeeAdmin)


# ############################### Medical Study Insurance Agreement
class MedicalStudyInsuranceAgreementResource(resources.ModelResource):

    class Meta:
        model = MedicalStudyInsuranceAgreement


class MedicalStudyInsuranceAgreementAdmin(ImportExportModelAdmin):
    resource_class = MedicalStudyInsuranceAgreementResource
    search_fields = ['id', 'insurance_plan__name', 'medical_study__name', 'coverage_percentage', 'medical_study__sector__name']
    list_filter = ['medical_study__sector', 'insurance_plan', 'medical_study', 'created_at', 'updated_at']

    list_display = ('id', 'insurance_plan', 'medical_study', 'coverage_percentage', 'cover_type', 'coverage_amount', 'currency', 'created_at', 'updated_at')


admin.site.register(MedicalStudyInsuranceAgreement, MedicalStudyInsuranceAgreementAdmin)


# ############################### Medical Supply Insurance Agreement
class MedicalSupplyInsuranceAgreementResource(resources.ModelResource):

    class Meta:
        model = MedicalSupplyInsuranceAgreement


class MedicalSupplyInsuranceAgreementAdmin(ImportExportModelAdmin):
    resource_class = MedicalSupplyInsuranceAgreementResource
    search_fields = ['id', 'insurance_plan__name', 'medical_supply__name', 'coverage_percentage']
    list_filter = ['insurance_plan', 'medical_supply', 'created_at', 'updated_at']

    list_display = ('id', 'insurance_plan', 'medical_supply', 'coverage_percentage', 'cover_type', 'coverage_amount', 'currency', 'created_at', 'updated_at')


admin.site.register(MedicalSupplyInsuranceAgreement, MedicalSupplyInsuranceAgreementAdmin)


# ############################### Sector
class SectorResource(resources.ModelResource):

    class Meta:
        model = Sector


class SectorAdmin(ImportExportModelAdmin):
    resource_class = SectorResource
    search_fields = ['id', 'name', 'sector_code']
    list_filter = ['created_at', 'updated_at']

    list_display = ('id', 'name', 'sector_code', 'created_at', 'updated_at')


admin.site.register(Sector, SectorAdmin)


# ############################### Insurance Plan Medical Stupply Fee
class InsurancePlanMedicalSupplyFeeResource(resources.ModelResource):

    class Meta:
        model = InsurancePlanMedicalSupplyFee


class InsurancePlanMedicalSupplyFeeAdmin(ImportExportModelAdmin):
    resource_class = InsurancePlanMedicalSupplyFeeResource
    search_fields = ['id', 'insurance_plan__name', 'medical_supply__name']
    list_filter = ['insurance_plan', 'medical_supply', 'currency', 'created_at', 'updated_at']

    list_display = ('id', 'insurance_plan', 'medical_supply', 'price', 'currency', 'created_at', 'updated_at')


admin.site.register(InsurancePlanMedicalSupplyFee, InsurancePlanMedicalSupplyFeeAdmin)
