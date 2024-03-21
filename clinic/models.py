import json

from django.contrib.auth.models import User
from django.core import serializers
from django.db import models
from softdelete.models import SoftDeleteObject
from django.utils.translation import ugettext_lazy as _
from auditlog.registry import auditlog
from base.models import Person, Currency, TimeStampModel
from colorfield.fields import ColorField

# Create your models here.


# INSURANCE COMPANY
from stock.models import Product


class InsuranceCompany(SoftDeleteObject, TimeStampModel):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    tax_identification_number = models.CharField(
        verbose_name=_('Tax Identification Number'),
        max_length=15,
        blank=True, null=True
    )
    email = models.EmailField(verbose_name=_('Email'),
                                       null=True, blank=False)
    address = models.CharField(verbose_name=_('Address'),
                                        max_length=250, null=True, blank=False)
    phone_number = models.CharField(verbose_name=_('Phone Number'),
                                             max_length=20, null=True, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Insurance")
        verbose_name_plural = _("Insurances")


auditlog.register(InsuranceCompany)


# INSURANCE PLAN
class InsurancePlan(SoftDeleteObject, TimeStampModel):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    insurance_company = models.ForeignKey(
        to=InsuranceCompany,
        on_delete=models.PROTECT,
        related_name="insurance_plans",
        verbose_name=_('Insurance Company'),
        null=False,
        blank=False
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Insurance Plan")
        verbose_name_plural = _("Insurance Plans")


auditlog.register(InsurancePlan)


# PATIENT
class Patient(SoftDeleteObject, Person, TimeStampModel):
    insurance_plan = models.ForeignKey(
        to=InsurancePlan,
        verbose_name=_('Insurance Plan'),
        null=True, blank=True,
        related_name='patients',
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = _('Patient')
        verbose_name_plural = _('Patients')

    def __str__(self):
        return self.name + ' ' + self.last_name + ' - ' + self.document_number

    def tojson(self):
        serialized_obj = serializers.serialize('json', [self, ])
        json_object = json.loads(serialized_obj)[0]
        return json_object


auditlog.register(Patient)


# DOCTOR SPECIALIZATION
class DoctorSpecialization(SoftDeleteObject, TimeStampModel):
    name = models.CharField(verbose_name=_('Name'), max_length=150, blank=False, null=False)

    class Meta:
        verbose_name = _('Doctor Specialization')
        verbose_name_plural = _('Doctors Specializations')

    def __str__(self):
        return self.name


auditlog.register(DoctorSpecialization)


# Sector
class Sector(SoftDeleteObject, TimeStampModel):
    name = models.CharField(max_length=100, verbose_name=_('Name'), null=False, blank=False)
    sector_code = models.CharField(verbose_name=_('Sector Code'), max_length=4, null=True, blank=True)

    class Meta:
        verbose_name = _('Sector')
        verbose_name_plural = _('Sectors')

    def __str__(self):
        return str(self.name)


auditlog.register(Sector)


# DOCTOR
class Doctor(SoftDeleteObject, Person, TimeStampModel):
    doctor_specializations = models.ManyToManyField(
        to=DoctorSpecialization,
        verbose_name=_('Specialization'),
        related_name='doctors',
        blank=True
    )
    tag_color = ColorField(default='#FF0000')
    sectors = models.ManyToManyField(
        to=Sector,
        verbose_name=_('Sectors'),
        related_name='doctors',
        blank=True
    )
    user = models.OneToOneField(
        to=User, on_delete=models.PROTECT,
        verbose_name=_('User'),
        related_name='doctor',
        null=True, blank=True
    )
    digital_signature = models.FileField(
        verbose_name=_('Digital Signature'),
        null=True, blank=True
    )

    class Meta:
        verbose_name = _('Doctor')
        verbose_name_plural = _('Doctors')

    def __str__(self):
        return self.name + ' ' + self.last_name


auditlog.register(Doctor)


# TREATING DOCTOR
class TreatingDoctor(SoftDeleteObject, Person, TimeStampModel):
    doctor_specializations = models.ManyToManyField(
        to=DoctorSpecialization,
        verbose_name=_('Specializations'),
        related_name='treating_doctors',
        blank=True
    )

    class Meta:
        verbose_name = _('Treating Doctor')
        verbose_name_plural = _('Treating Doctors')

    def __str__(self):
        return self.name + ' ' + self.last_name


auditlog.register(TreatingDoctor)


# TECHNICIAN SPECIALIZATION
class TechnicianSpecialization(SoftDeleteObject, TimeStampModel):
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False, blank=False)

    class Meta:
        verbose_name = _('Technician Specialization')
        verbose_name_plural = _('Technician Specialization')

    def __str__(self):
        return self.name


auditlog.register(TechnicianSpecialization)


# TECHNICIAN
class Technician(SoftDeleteObject, Person, TimeStampModel):
    technician_specializations = models.ManyToManyField(
        to=TechnicianSpecialization,
        verbose_name=_('Specializations'),
        related_name='technicians',
        blank=True
    )
    sectors = models.ManyToManyField(
        to=Sector,
        verbose_name=_('Sectors'),
        related_name='technicians',
        blank=True
    )

    class Meta:
        verbose_name = _('Technician')
        verbose_name_plural = _('Technicians')

    def __str__(self):
        return self.name + ' ' + self.last_name


auditlog.register(Technician)


# MEDICAL STUDY TYPE
class MedicalStudyType(SoftDeleteObject, TimeStampModel):
    name = models.CharField(max_length=100, verbose_name=_('Name'), blank=False, null=False)

    class Meta:
        verbose_name = _('Medical Study Type')
        verbose_name_plural = _('Medical Studies Types ')

    def __str__(self):
        return self.name


auditlog.register(MedicalStudyType)


# Medical Equipment Type
class MedicalEquipmentType(SoftDeleteObject, TimeStampModel):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=100,
        null=False, blank=False
    )
    equipment_type_code = models.CharField(
        verbose_name=_('Equipment Type Code'),
        max_length=4,
        null=True, blank=True
    )

    class Meta:
        verbose_name = _('Medical Equipment Type')
        verbose_name_plural = _('Medical Equipment Types')

    def __str__(self):
        return self.name


auditlog.register(MedicalEquipmentType)


# MEDICAL STUDY
class MedicalStudy(SoftDeleteObject, TimeStampModel):
    name = models.CharField(max_length=100, verbose_name=_('Name'), null=False, blank=False)
    type = models.ForeignKey(
        to=MedicalStudyType,
        on_delete=models.PROTECT,
        null=False, blank=False,
        verbose_name=_('Medical Study Type'),
        related_name='medical_studies',
    )
    duration_in_minutes = models.IntegerField(
        verbose_name=_('Time Duration in minutes'),
        null=False, blank=False,
        default=30
    )
    # equipment_type_used = models.ForeignKey(
    #     to=MedicalEquipmentType,
    #     on_delete=models.PROTECT,
    #     null=False, blank=False,
    #     verbose_name=_('Medical Equipment Type Used'),
    #     related_name='medical_studies',
    # )
    price = models.FloatField(
        verbose_name=_('Price'),
        null=False, blank=False,
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False
    )
    sector = models.ForeignKey(
        to=Sector, on_delete=models.PROTECT,
        verbose_name=_('Sector'),
        related_name='medical_studies',
        null=True, blank=True,
        default=None,
    )

    class Meta:
        verbose_name = _('Medical Study')
        verbose_name_plural = _('Medical Studies')

    def __str__(self):
        return self.name

    def tojson(self):
        serialized_obj = serializers.serialize('json', [self, ])
        json_object = json.loads(serialized_obj)[0]
        return json_object


auditlog.register(MedicalStudy)


# MEDICAL EQUIPMENT
class MedicalEquipment(SoftDeleteObject, TimeStampModel):
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False, blank=False)
    # type = models.ForeignKey(
    #     to=MedicalEquipmentType, on_delete=models.PROTECT,
    #     verbose_name=_('Type'),
    #     null=False, blank=False,
    #     related_name='medical_equipments'
    # )
    tag_color = ColorField(default='#FF0000')
    sector = models.ForeignKey(
        to=Sector, on_delete=models.PROTECT,
        verbose_name=_('Sector'),
        related_name='medical_equipments',
        null=True, blank=True,
        default=None,
    )

    class Meta:
        verbose_name = _('Medical Equipment')
        verbose_name_plural = _('Medical Equipments')

    def __str__(self):
        return self.name


auditlog.register(MedicalEquipment)


# Doctor Medical Study
class DoctorMedicalStudy(SoftDeleteObject, TimeStampModel):
    doctor = models.ForeignKey(
        to=Doctor, on_delete=models.PROTECT,
        null=False, blank=False,
        verbose_name=_('Doctor'),
        related_name='doctor_medical_studies'
    )
    medical_study = models.ForeignKey(
        to=MedicalStudy, on_delete=models.PROTECT,
        null=False, blank=False,
        verbose_name=_('Medical Study'),
        related_name='doctor_medical_studies',
    )

    class Meta:
        verbose_name = _('Doctor Medical Study')
        verbose_name_plural = _('Doctor Medical Studies')
        unique_together = ('doctor', 'medical_study')

    def __str__(self):
        return str(self.doctor) + ' - ' + self.medical_study.name


auditlog.register(DoctorMedicalStudy)


# Insurance PlanMedical Study Fee
class InsurancePlanMedicalStudyFee(SoftDeleteObject, TimeStampModel):
    insurance_plan = models.ForeignKey(
        to=InsurancePlan, on_delete=models.PROTECT,
        verbose_name=_('Insurance Plan'),
        null=False, blank=False,
        related_name='insurance_plan_medical_study_fees'
    )
    medical_study = models.ForeignKey(
        to=MedicalStudy, on_delete=models.PROTECT,
        verbose_name=_('Medical Study'),
        null=False, blank=False,
        related_name='insurance_plan_medical_study_fees'
    )
    price = models.FloatField(
        verbose_name=_('Price'),
        null=False, blank=False,
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('Insurance Plan Medical Study Fee')
        verbose_name_plural = _('Insurance Plan Medical Study Fees')

    def __str__(self):
        return str(self.insurance_plan) + ' - ' + str(self.medical_study)


# Medical Study Insurance Agreement
class MedicalStudyInsuranceAgreement(SoftDeleteObject, TimeStampModel):
    medical_study = models.ForeignKey(
        to=MedicalStudy, on_delete=models.PROTECT,
        verbose_name=_('Medical Study'),
        null=False, blank=False,
        related_name='medical_study_insurance_agreements'
    )
    insurance_plan = models.ForeignKey(
        to=InsurancePlan, on_delete=models.PROTECT,
        verbose_name=_('Insurance Plan'),
        null=False, blank=False,
        related_name='medical_study_insurance_agreements'
    )
    COVER_TYPES = (
        (0, _('Percentage')),
        (1, _('Amount')),
    )
    cover_type = models.IntegerField(verbose_name=_('Cover Types'), choices=COVER_TYPES, null=False, blank=False, default=0)
    coverage_percentage = models.FloatField(
        verbose_name=_('Coverage Percentage'),
        default=0
    )
    coverage_amount = models.FloatField(
        verbose_name=_('Coverage Amount'),
        default=0
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='medical_study_insurance_agreements',
        default=1
    )

    class Meta:
        verbose_name = _('Medical Study Insurance Agreement')
        verbose_name_plural = _('Medical Studys Insurances Agreements')
        unique_together = ('medical_study', 'insurance_plan')

    def __str__(self):
        return str(self.medical_study) + ' - ' + str(self.insurance_plan) + " - " + str(self.coverage_percentage) + "%"

    def patient_percentage_to_pay(self):
        return 100 - self.coverage_percentage


auditlog.register(MedicalStudyInsuranceAgreement)


# Medical Supply Insurance Agreement
class MedicalSupplyInsuranceAgreement(SoftDeleteObject, TimeStampModel):
    medical_supply = models.ForeignKey(
        to=Product, on_delete=models.PROTECT,
        verbose_name=_('Medical Supply'),
        null=False, blank=False,
        related_name='medical_supply_insurance_agreements'
    )
    insurance_plan = models.ForeignKey(
        to=InsurancePlan, on_delete=models.PROTECT,
        verbose_name=_('Insurance Plan'),
        null=False, blank=False,
        related_name='medical_supply_insurance_agreements'
    )
    COVER_TYPES = (
        (0, _('Percentage')),
        (1, _('Amount')),
    )
    cover_type = models.IntegerField(verbose_name=_('Cover Types'), choices=COVER_TYPES, null=False, blank=False, default=0)
    coverage_percentage = models.FloatField(
        verbose_name=_('Coverage Percentage'),
        default=0
    )
    coverage_amount = models.FloatField(
        verbose_name=_('Coverage Amount'),
        default=0
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='medical_supply_insurance_agreements',
        default=1
    )

    class Meta:
        verbose_name = _('Medical Supply Insurance Agreement')
        verbose_name_plural = _('Medical Supplies Insurances Agreements')
        unique_together = ('medical_supply', 'insurance_plan')

    def __str__(self):
        return str(self.medical_supply) + ' - ' + str(self.insurance_plan) + " - " + str(self.coverage_percentage) + "%"

    def patient_percentage_to_pay(self):
        return 100 - self.coverage_percentage


auditlog.register(MedicalSupplyInsuranceAgreement)


# Insurance PlanMedical Supply Fee
class InsurancePlanMedicalSupplyFee(SoftDeleteObject, TimeStampModel):
    insurance_plan = models.ForeignKey(
        to=InsurancePlan, on_delete=models.PROTECT,
        verbose_name=_('Insurance Plan'),
        null=False, blank=False,
        related_name='insurance_plan_medical_supply_fees'
    )
    medical_supply = models.ForeignKey(
        to=Product, on_delete=models.PROTECT,
        verbose_name=_('Medical Supply'),
        null=False, blank=False,
        related_name='insurance_plan_medical_supply_fees'
    )
    price = models.FloatField(
        verbose_name=_('Price'),
        null=False, blank=False,
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False
    )

    class Meta:
        verbose_name = _('Insurance Plan Medical Supply Fee')
        verbose_name_plural = _('Insurance Plan Medical Supplies Fees')

    def __str__(self):
        return str(self.insurance_plan) + ' - ' + str(self.medical_supply)


auditlog.register(InsurancePlanMedicalSupplyFee)
