from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, Row, Column, ButtonHolder, Submit, HTML, Field
from django import forms
from django.forms import inlineformset_factory
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from ckeditor.widgets import CKEditorWidget

from base.models import Currency, Person
from clinic.models import Patient, InsurancePlan, TreatingDoctor, Doctor, Technician
from consultation.models import ConsultationSheet, ConsultationSheetDocument, MedicalSupplyUsed, ConsultationState, \
    ConsultationEntrySheet, Consultation, ConsultationReport, DoctorReportTemplate, ConsultationFile
from sales.models import ConsultationSheetSalePayment, ConsultationEntrySheetSaleHeader
from scheduling.models import Appointment


# ###################################  CREATE FORM
from stock.models import Product


class ConsultationSheetCreateForm(forms.ModelForm):
    MALE_CODE = 0
    FEMALE_CODE = 1

    SEX_CODES = (
        (MALE_CODE, _('Male')),
        (FEMALE_CODE, _('Female')),
    )

    currency = forms.CharField(widget=forms.HiddenInput())
    consultation_state = forms.CharField(widget=forms.HiddenInput())
    medical_study_ammount = forms.CharField(
        label=_('Medical Study Ammount'),
    )
    medical_supplies_ammount = forms.CharField(
        label=_('Medical Supplies Ammount'),
    )
    total_amount = forms.CharField(
        label=_('Total Amount'),
    )
    medical_study_ammount_to_pay_insurance = forms.CharField(
        label=_('Medical Study Amount to Pay Insurance')
    )
    medical_study_ammount_to_pay_patient = forms.CharField(
        label=_('Medical Study Amount to Pay Patient')
    )
    medical_supplies_ammount_to_pay_insurance = forms.CharField(
        label=_('Medical Supplies Amount to Pay Insurance')
    )
    medical_supplies_ammount_to_pay_patient = forms.CharField(
        label=_('Medical Supplies Amount to Pay Patient')
    )
    total_ammount_to_pay_insurance = forms.CharField(
        label=_('Total Amount to Pay Insurance')
    )
    total_ammount_to_pay_patient = forms.CharField(
        label=_('Total Amount to Pay Patient')
    )
    discount = forms.CharField(
        label=_('Discount'), required=False
    )
    total_ammount_to_pay_patient_with_discount = forms.CharField(
        label=_('Total Amount to Pay Patient with discount')
    )

    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
                'readonly': True
            })
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    # New Patient
    new_patient = forms.BooleanField(
        label=_('New Patient'),
        required=False,
    )
    patient_name = forms.CharField(
        label=_('Patient Name'),
        required=True,
    )
    patient_last_name = forms.CharField(
        label=_('Patient Last Name'),
        required=True,
    )
    patient_sex = forms.ChoiceField(
        label=_('Sex'),
        required=True,
        choices=SEX_CODES
    )
    patient_document_number = forms.CharField(
        label=_('Patient Document Number'),
        required=True,
    )
    patient_birth_date = forms.DateField(
        required=True,
        label=_('Birth Date'),
        widget=forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'}),
    )
    patient_weight = forms.CharField(
        required=True,
        label=_('Weight')
    )
    patient_city = forms.ChoiceField(
        required=True,
        label=_('City'),
        choices=Person.CITYS
    )
    patient_address = forms.CharField(
        required=False,
        label=_('Address'),
    )
    COVER_TYPES = (
        (0, _('Percentage')),
        (1, _('Amount')),
    )
    study_cover_type = forms.ChoiceField(
        label=_('Study Cover Type'),
        choices=COVER_TYPES,
        required=True
    )
    insurance_agreement_coverage_percent = forms.CharField(
        required=False,
        label=_('Insurance Agreement Coverage Percent'),
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 80'}),
    )
    insurance_agreement_coverage_amount = forms.CharField(
        required=False,
        label=_('Insurance Agreement Coverage Amount'),
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 100.000'}),
    )
    # New Treating doctor
    new_treating_doctor = forms.BooleanField(
        label=_('New Treating Doctor'),
        required=False,
    )
    treating_doctor_name = forms.CharField(
        label=_('Treating Doctor Name'),
        required=False,
    )
    treating_doctor_last_name = forms.CharField(
        label=_('Treating Doctor Last Name'),
        required=False,
    )
    treating_doctor_sex = forms.ChoiceField(
        label=_('Sex'),
        required=False,
        choices=SEX_CODES
    )
    amount_paid = forms.CharField(
        required=False,
        label=_('Amount Paid'),
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 100.000'}),
    )
    patient_balance = forms.CharField(
        required=False,
        label=_('Patient Balance'),
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 100.000'}),
    )

    class Meta:
        model = ConsultationSheet
        fields = [
            'consultation_date',
            'patient',
            'contact_number',
            'contact_email',
            'patient_insurance_plan',
            'medical_study',
            'study_cover_type',
            'insurance_agreement_coverage_percent',
            'insurance_agreement_coverage_amount',
            'medical_equipment',
            'doctor',
            'technician',
            'medical_study_ammount',
            'medical_study_ammount_to_pay_insurance',
            'medical_study_ammount_to_pay_patient',
            'medical_supplies_ammount',
            'medical_supplies_ammount_to_pay_insurance',
            'medical_supplies_ammount_to_pay_patient',
            'total_amount',
            'total_ammount_to_pay_insurance',
            'total_ammount_to_pay_patient',
            'discount',
            'total_ammount_to_pay_patient_with_discount',
            'currency',
            'payment_method',
            'payment_reference',
            'treating_doctor',
            'reporting_doctor',
            'consultation_state',
            'internal_results_delivery_date',
            'patient_results_delivery_date',
            'observations',
            'amount_paid',
            'patient_balance'
        ]

    def __init__(self, *args, **kwargs):
        super(ConsultationSheetCreateForm, self).__init__(*args, **kwargs)
        self.fields['medical_study_ammount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_study_ammount'].widget.attrs['readonly'] = True
        self.fields['medical_supplies_ammount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_supplies_ammount'].widget.attrs['readonly'] = True
        self.fields['total_amount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_amount'].widget.attrs['readonly'] = True

        self.fields['study_cover_type'].widget.attrs.update({'class': 'study_cover_type'})
        self.fields['insurance_agreement_coverage_percent'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['insurance_agreement_coverage_percent'].widget.attrs.update(
            {'class': 'study_insurance_agreement_coverage_percent'})
        self.fields['insurance_agreement_coverage_amount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['insurance_agreement_coverage_amount'].widget.attrs.update(
            {'class': 'study_insurance_agreement_coverage_amount'})

        self.fields['medical_study_ammount_to_pay_insurance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_study_ammount_to_pay_insurance'].widget.attrs['readonly'] = True
        self.fields['medical_study_ammount_to_pay_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_study_ammount_to_pay_patient'].widget.attrs['readonly'] = True

        self.fields['medical_supplies_ammount_to_pay_insurance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_supplies_ammount_to_pay_insurance'].widget.attrs['readonly'] = True
        self.fields['medical_supplies_ammount_to_pay_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_supplies_ammount_to_pay_patient'].widget.attrs['readonly'] = True

        self.fields['total_ammount_to_pay_insurance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_ammount_to_pay_insurance'].widget.attrs['readonly'] = True
        self.fields['total_ammount_to_pay_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_ammount_to_pay_patient'].widget.attrs['readonly'] = True
        self.fields['total_ammount_to_pay_patient_with_discount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_ammount_to_pay_patient_with_discount'].widget.attrs['readonly'] = True

        self.fields['discount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['amount_paid'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['patient_balance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['patient_balance'].widget.attrs['readonly'] = True

        self.fields['patient_name'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['patient_name'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['patient_last_name'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['patient_last_name'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['patient_address'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['patient_address'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['contact_email'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['contact_email'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['treating_doctor_name'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['treating_doctor_name'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['treating_doctor_last_name'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['treating_doctor_last_name'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['observations'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['observations'].widget.attrs.update({'class': 'to-upper-case'})

    def clean_currency(self):
        currency_name = self.data['currency']
        currency = Currency.objects.get(name=currency_name)
        return currency

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient

    def clean_appointment(self):
        appointment_id = self.data['appointment']
        appointment = None
        if appointment_id != '' or appointment_id is not None:
            appointment = Appointment.objects.get(pk=appointment_id)
        return appointment

    def clean_consultation_state(self):
        consultation_state_id = self.data['consultation_state']
        consultation_state = None
        if consultation_state_id != '' or consultation_state_id is not None:
            consultation_state = ConsultationState.objects.get(pk=consultation_state_id)
        return consultation_state

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient


class MedicalSupplyUsedCreateForm(forms.ModelForm):
    currency = forms.CharField(widget=forms.HiddenInput())
    quantity = forms.CharField(
        label=_('Quantity'),
    )
    price = forms.CharField(
        label=_('Price'),
    )
    total_price = forms.CharField(
        label=_('Total'),
    )
    ammount_to_pay_insurance = forms.CharField(
        label=_('Amount To Pay Insurance'),
    )
    ammount_to_pay_patient = forms.CharField(
        label=_('Amount To Pay Patient'),
    )
    COVER_TYPES = (
        (0, _('Percentage')),
        (1, _('Amount')),
    )
    cover_type = forms.ChoiceField(
        label=_('Cover Type'),
        choices=COVER_TYPES,
        required=True
    )
    insurance_agreement_coverage_amount = forms.CharField(
        label=_('Insurance Agreement Coverage Amount'),
        required=False
    )

    class Meta:
        model = MedicalSupplyUsed
        fields = [
            'medical_supply',
            'quantity',
            'price',
            'total_price',
            'cover_type',
            'insurance_agreement_coverage_percent',
            'insurance_agreement_coverage_amount',
            'ammount_to_pay_insurance',
            'ammount_to_pay_patient',
            'currency'
        ]

    def clean_currency(self):
        currency_name = self.data['currency']
        currency = Currency.objects.get(name=currency_name)
        return currency

    def __init__(self, *args, **kwargs):
        super(MedicalSupplyUsedCreateForm, self).__init__(*args, **kwargs)
        self.fields['medical_supply'].widget.attrs['class'] = 'select medical_supply_select'
        self.fields['currency'].widget.attrs['class'] = 'medical_supply_currency'
        self.fields['price'].widget.attrs['class'] = 'medical_supply_price'
        self.fields['price'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['price'].widget.attrs['readonly'] = True
        self.fields['total_price'].widget.attrs['class'] = 'medical_supply_total_price'
        self.fields['total_price'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_price'].widget.attrs['readonly'] = True
        self.fields['quantity'].widget.attrs['class'] = 'medical_supply_quantity'
        self.fields['quantity'].widget.attrs.update({'style': 'text-align: right;'})

        self.fields['insurance_agreement_coverage_percent'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['insurance_agreement_coverage_percent'].widget.attrs['class'] = \
            'insurance_agreement_coverage_percent'
        self.fields['insurance_agreement_coverage_amount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['insurance_agreement_coverage_amount'].widget.attrs['class'] = 'insurance_agreement_coverage_amount'
        self.fields['ammount_to_pay_insurance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['ammount_to_pay_insurance'].widget.attrs['class'] = 'ammount_to_pay_insurance'
        self.fields['ammount_to_pay_insurance'].widget.attrs['readonly'] = True
        self.fields['ammount_to_pay_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['ammount_to_pay_patient'].widget.attrs['class'] = 'ammount_to_pay_patient'
        self.fields['ammount_to_pay_patient'].widget.attrs['readonly'] = True
        self.fields['cover_type'].widget.attrs['class'] = 'cover_type'


class ConsultationSheetDocumentForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'data-height': '200', 'data-default-file': ''}),
        label=_('File')
    )

    class Meta:
        model = ConsultationSheetDocument
        fields = [
            'document_type',
            'file',
        ]

    def __init__(self, *args, **kwargs):
        super(ConsultationSheetDocumentForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'dropify'


ConsultationSheetDocumentFormSet = inlineformset_factory(
    ConsultationSheet, ConsultationSheetDocument, ConsultationSheetDocumentForm,
    fields=('document_type', 'file'),
    extra=1,
)

MedicalSupplyUsedCreateFormSet = inlineformset_factory(
    ConsultationSheet, MedicalSupplyUsed, MedicalSupplyUsedCreateForm,
    extra=1,
)


# ###################################  UPDATE FORM
class ConsultationSheetUpdateForm(forms.ModelForm):
    currency = forms.CharField(widget=forms.HiddenInput())
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
                'readonly': True
            })
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    consultation_state = forms.CharField(widget=forms.HiddenInput())
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
                'readonly': True
            })
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    medical_study_ammount = forms.CharField(
        label=_('Medical Study Ammount'),
    )
    medical_supplies_ammount = forms.CharField(
        label=_('Medical Supplies Ammount'),
    )
    total_amount = forms.CharField(
        label=_('Total Amount'),
    )
    medical_study_ammount_to_pay_insurance = forms.CharField(
        label=_('Medical Study Amount to Pay Insurance')
    )
    medical_study_ammount_to_pay_patient = forms.CharField(
        label=_('Medical Study Amount to Pay Patient')
    )
    medical_supplies_ammount_to_pay_insurance = forms.CharField(
        label=_('Medical Supplies Amount to Pay Insurance')
    )
    medical_supplies_ammount_to_pay_patient = forms.CharField(
        label=_('Medical Supplies Amount to Pay Patient')
    )
    total_ammount_to_pay_insurance = forms.CharField(
        label=_('Total Amount to Pay Insurance')
    )
    total_ammount_to_pay_patient = forms.CharField(
        label=_('Total Amount to Pay Patient')
    )
    discount = forms.CharField(
        label=_('Discount'), required=False
    )
    total_ammount_to_pay_patient_with_discount = forms.CharField(
        label=_('Total Amount to Pay Patient with discount')
    )
    COVER_TYPES = (
        (0, _('Percentage')),
        (1, _('Amount')),
    )
    study_cover_type = forms.ChoiceField(
        label=_('Study Cover Type'),
        choices=COVER_TYPES,
        required=True
    )
    insurance_agreement_coverage_percent = forms.CharField(
        required=False,
        label=_('Insurance Agreement Coverage Percent'),
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 80'}),
    )
    insurance_agreement_coverage_amount = forms.CharField(
        required=False,
        label=_('Insurance Agreement Coverage Amount'),
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 100.000'}),
    )
    amount_paid = forms.CharField(
        required=False,
        label=_('Amount Paid'),
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 100.000'}),
    )
    patient_balance = forms.CharField(
        required=False,
        label=_('Patient Balance'),
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 100.000'}),
    )

    class Meta:
        model = ConsultationSheet
        fields = [
            'consultation_date',
            'patient',
            'contact_number',
            'contact_email',
            'patient_insurance_plan',
            'medical_study',
            'study_cover_type',
            'insurance_agreement_coverage_percent',
            'insurance_agreement_coverage_amount',
            'medical_equipment',
            'doctor',
            'technician',
            'medical_study_ammount',
            'medical_study_ammount_to_pay_insurance',
            'medical_study_ammount_to_pay_patient',
            'medical_supplies_ammount',
            'medical_supplies_ammount_to_pay_insurance',
            'medical_supplies_ammount_to_pay_patient',
            'total_amount',
            'total_ammount_to_pay_insurance',
            'total_ammount_to_pay_patient',
            'discount',
            'total_ammount_to_pay_patient_with_discount',
            'currency',
            'payment_method',
            'payment_reference',
            'treating_doctor',
            'reporting_doctor',
            'consultation_state',
            'received_by',
            'internal_results_delivery_date',
            'patient_results_delivery_date',
            'observations',
            'amount_paid',
            'patient_balance'
        ]

    def __init__(self, *args, **kwargs):
        super(ConsultationSheetUpdateForm, self).__init__(*args, **kwargs)
        self.fields['medical_study_ammount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_study_ammount'].widget.attrs['readonly'] = True
        self.fields['medical_supplies_ammount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_supplies_ammount'].widget.attrs['readonly'] = True
        self.fields['total_amount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_amount'].widget.attrs['readonly'] = True

        self.fields['study_cover_type'].widget.attrs.update({'class': 'study_cover_type'})
        self.fields['insurance_agreement_coverage_percent'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['insurance_agreement_coverage_percent'].widget.attrs.update(
            {'class': 'study_insurance_agreement_coverage_percent'})
        self.fields['insurance_agreement_coverage_amount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['insurance_agreement_coverage_amount'].widget.attrs.update(
            {'class': 'study_insurance_agreement_coverage_amount'})

        self.fields['medical_study_ammount_to_pay_insurance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_study_ammount_to_pay_insurance'].widget.attrs['readonly'] = True
        self.fields['medical_study_ammount_to_pay_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_study_ammount_to_pay_patient'].widget.attrs['readonly'] = True

        self.fields['medical_supplies_ammount_to_pay_insurance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_supplies_ammount_to_pay_insurance'].widget.attrs['readonly'] = True
        self.fields['medical_supplies_ammount_to_pay_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_supplies_ammount_to_pay_patient'].widget.attrs['readonly'] = True

        self.fields['total_ammount_to_pay_insurance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_ammount_to_pay_insurance'].widget.attrs['readonly'] = True
        self.fields['total_ammount_to_pay_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_ammount_to_pay_patient'].widget.attrs['readonly'] = True
        self.fields['total_ammount_to_pay_patient_with_discount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_ammount_to_pay_patient_with_discount'].widget.attrs['readonly'] = True
        # self.fields['amount_paid'].widget.attrs['readonly'] = True
        # self.fields['patient_balance'].widget.attrs['readonly'] = True

        self.fields['discount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['amount_paid'].widget.attrs.update({'style': 'text-align: right;'})
        # self.fields['amount_paid'].widget.attrs['readonly'] = True
        self.fields['patient_balance'].widget.attrs.update({'style': 'text-align: right;'})
        # self.fields['patient_balance'].widget.attrs['readonly'] = True

        self.fields['contact_email'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['contact_email'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['observations'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['observations'].widget.attrs.update({'class': 'to-upper-case'})

    def clean_currency(self):
        currency_id = self.data['currency']
        currency = Currency.objects.get(pk=currency_id)
        return currency

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient

    def clean_consultation_state(self):
        consultation_state_id = self.data['consultation_state']
        consultation_state = None
        if consultation_state_id != '' or consultation_state_id is not None:
            consultation_state = ConsultationState.objects.get(pk=consultation_state_id)
        return consultation_state

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient


class MedicalSupplyUsedUpdateForm(forms.ModelForm):
    currency = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    quantity = forms.CharField(
        label=_('Quantity'),
        # required=False
    )
    price = forms.CharField(
        label=_('Price'),
        # required=False
    )
    total_price = forms.CharField(
        label=_('Total'),
        # required=False
    )
    ammount_to_pay_insurance = forms.CharField(
        label=_('Amount To Pay Insurance'),
        # required=False
    )
    ammount_to_pay_patient = forms.CharField(
        label=_('Amount To Pay Patient'),
        # required=False
    )
    COVER_TYPES = (
        (0, _('Percentage')),
        (1, _('Amount')),
    )
    cover_type = forms.ChoiceField(
        label=_('Cover Type'),
        choices=COVER_TYPES,
        # required=False
    )
    insurance_agreement_coverage_amount = forms.CharField(
        label=_('Insurance Agreement Coverage Amount'),
        # required=False
    )
    insurance_agreement_coverage_percent = forms.CharField(
        label=_('Insurance Agreement Coverage Percent'),
        # required=False
    )
    medical_supply = forms.ModelChoiceField(
        label=_('Medical Supply'),
        # required=False,
        queryset=Product.objects.all()
    )

    class Meta:
        model = MedicalSupplyUsed
        fields = [
            'medical_supply',
            'quantity',
            'price',
            'total_price',
            'cover_type',
            'insurance_agreement_coverage_percent',
            'insurance_agreement_coverage_amount',
            'ammount_to_pay_insurance',
            'ammount_to_pay_patient',
            'currency'
        ]

    def __init__(self, *args, **kwargs):
        super(MedicalSupplyUsedUpdateForm, self).__init__(*args, **kwargs)
        self.fields['medical_supply'].widget.attrs['class'] = 'select medical_supply_select'
        self.fields['currency'].widget.attrs['class'] = 'medical_supply_currency'
        self.fields['price'].widget.attrs['class'] = 'medical_supply_price'
        self.fields['price'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['price'].widget.attrs['readonly'] = True
        self.fields['total_price'].widget.attrs['class'] = 'medical_supply_total_price'
        self.fields['total_price'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_price'].widget.attrs['readonly'] = True
        self.fields['quantity'].widget.attrs['class'] = 'medical_supply_quantity'
        self.fields['quantity'].widget.attrs.update({'style': 'text-align: right;'})

        self.fields['insurance_agreement_coverage_percent'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['insurance_agreement_coverage_percent'].widget.attrs['class'] = \
            'insurance_agreement_coverage_percent'
        self.fields['insurance_agreement_coverage_amount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['insurance_agreement_coverage_amount'].widget.attrs['class'] = 'insurance_agreement_coverage_amount'
        self.fields['ammount_to_pay_insurance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['ammount_to_pay_insurance'].widget.attrs['class'] = 'ammount_to_pay_insurance'
        self.fields['ammount_to_pay_insurance'].widget.attrs['readonly'] = True
        self.fields['ammount_to_pay_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['ammount_to_pay_patient'].widget.attrs['class'] = 'ammount_to_pay_patient'
        self.fields['ammount_to_pay_patient'].widget.attrs['readonly'] = True
        self.fields['cover_type'].widget.attrs['class'] = 'cover_type'

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['medical_supply'].widget.attrs['disabled'] = True
            self.fields['price'].widget.attrs['readonly'] = True
            self.fields['quantity'].widget.attrs['readonly'] = True
            self.fields['insurance_agreement_coverage_percent'].widget.attrs['readonly'] = True
            self.fields['insurance_agreement_coverage_amount'].widget.attrs['readonly'] = True
            self.fields['cover_type'].widget.attrs['disabled'] = True

    def clean_currency(self):
        currency_id = self.data['currency']
        currency = Currency.objects.get(pk=currency_id)
        return currency


MedicalSupplyUsedUpdateFormSet = inlineformset_factory(
    ConsultationSheet, MedicalSupplyUsed, MedicalSupplyUsedUpdateForm,
    extra=1,
)


class ConsultationEntrySheetCreateForm(forms.ModelForm):
    MALE_CODE = 0
    FEMALE_CODE = 1

    SEX_CODES = (
        (MALE_CODE, _('Male')),
        (FEMALE_CODE, _('Female')),
    )
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
            })
    )
    patient = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    # New Patient
    new_patient = forms.BooleanField(
        label=_('New Patient'),
        required=False,
    )
    patient_name = forms.CharField(
        label=_('Patient Name'),
        required=True,
    )
    patient_last_name = forms.CharField(
        label=_('Patient Last Name'),
        required=True,
    )
    patient_sex = forms.ChoiceField(
        label=_('Sex'),
        required=True,
        choices=SEX_CODES
    )
    patient_document_number = forms.CharField(
        label=_('Document Number'),
        required=True,
    )
    # invoicing
    patient_tax_identification_number = forms.CharField(
        label=_('Tax Identification Number'),
        required=True,
    )
    patient_tax_identification_name = forms.CharField(
        label=_('Tax Identification Name'),
        required=True,
    )
    patient_phone_number = forms.CharField(
        label=_('Phone Number'),
        required=True,
    )
    patient_address = forms.CharField(
        required=True,
        label=_('Address'),
    )
    patient_email = forms.CharField(
        label=_('Email'),
        required=True,
    )
    patient_is_taxpayer = forms.BooleanField(
        label=_('Patient Is Taxpayer'),
        required=False,
    )
    patient_birth_date = forms.DateField(
        required=True,
        label=_('Birth Date'),
        widget=forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'}),
    )
    patient_weight = forms.CharField(
        required=True,
        label=_('Weight')
    )
    patient_city = forms.ChoiceField(
        required=True,
        label=_('City'),
        choices=Person.CITYS
    )
    patient_insurance_plan = forms.ModelChoiceField(
        queryset=InsurancePlan.objects.all(),
        label=_('Insurance Plan'),
        required=False,
    )
    currency = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = ConsultationEntrySheet
        fields = [
            'consultation_entry_sheet_date',
            'patient',
            'currency'
        ]

    def __init__(self, *args, **kwargs):
        super(ConsultationEntrySheetCreateForm, self).__init__(*args, **kwargs)
        self.fields['patient_name'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['patient_name'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['patient_last_name'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['patient_last_name'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['patient_address'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['patient_address'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['patient_email'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['patient_email'].widget.attrs.update({'class': 'to-upper-case'})

    def clean_currency(self):
        currency_id = self.data['currency']
        currency = Currency.objects.get(pk=currency_id)
        return currency

    def clean_patient(self):
        patient_id = self.data['patient']
        if patient_id != '':
            patient = Patient.objects.get(pk=patient_id)
        else:
            patient = None
        return patient


class ConsultationEntrySheetUpdateForm(forms.ModelForm):
    MALE_CODE = 0
    FEMALE_CODE = 1

    SEX_CODES = (
        (MALE_CODE, _('Male')),
        (FEMALE_CODE, _('Female')),
    )
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Escriba aquí el nombre o CI del paciente', 'readonly': True})
    )
    patient = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    # New Patient
    new_patient = forms.BooleanField(
        label=_('New Patient'),
        required=False,
    )
    patient_name = forms.CharField(
        label=_('Patient Name'),
        required=True,
    )
    patient_last_name = forms.CharField(
        label=_('Patient Last Name'),
        required=True,
    )
    patient_sex = forms.ChoiceField(
        label=_('Sex'),
        required=True,
        choices=SEX_CODES
    )
    patient_document_number = forms.CharField(
        label=_('Document Number'),
        required=True,
    )
    # invoicing
    patient_tax_identification_number = forms.CharField(
        label=_('Tax Identification Number'),
        required=True,
    )
    patient_tax_identification_name = forms.CharField(
        label=_('Tax Identification Name'),
        required=True,
    )
    patient_phone_number = forms.CharField(
        label=_('Phone Number'),
        required=True,
    )
    patient_address = forms.CharField(
        required=True,
        label=_('Address'),
    )
    patient_email = forms.CharField(
        label=_('Email'),
        required=True,
    )
    patient_is_taxpayer = forms.BooleanField(
        label=_('Patient Is Taxpayer'),
        required=False,
    )

    patient_birth_date = forms.DateField(
        required=True,
        label=_('Birth Date'),
        widget=forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'}),
    )
    patient_weight = forms.CharField(
        required=True,
        label=_('Weight')
    )
    patient_city = forms.ChoiceField(
        required=True,
        label=_('City'),
        choices=Person.CITYS
    )
    patient_insurance_plan = forms.ModelChoiceField(
        queryset=InsurancePlan.objects.all(),
        label=_('Insurance Plan'),
        required=False,
    )
    total_amount = forms.CharField(
        label=_('Total Amount')
    )
    total_amount_to_pay_insurance = forms.CharField(
        label=_('Total Amount to pay Insurance')
    )
    total_amount_to_pay_patient = forms.CharField(
        label=_('Total Amount to pay Patient')
    )
    total_amount_paid_by_patient = forms.CharField(
        label=_('Total Amount paid by Patient')
    )
    patient_balance = forms.CharField(
        label=_('Patient Balance')
    )

    class Meta:
        model = ConsultationEntrySheet
        fields = [
            'consultation_entry_sheet_date',
            'patient',
            'total_amount',
            'total_amount_to_pay_insurance',
            'total_amount_to_pay_patient',
            'total_amount_paid_by_patient',
            'patient_balance'
        ]

    def __init__(self, *args, **kwargs):
        super(ConsultationEntrySheetUpdateForm, self).__init__(*args, **kwargs)
        # self.fields['patient'].widget.attrs['disabled'] = True

        self.fields['total_amount'].widget.attrs['readonly'] = True
        self.fields['total_amount_to_pay_insurance'].widget.attrs['readonly'] = True
        self.fields['total_amount_to_pay_patient'].widget.attrs['readonly'] = True
        self.fields['total_amount_paid_by_patient'].widget.attrs['readonly'] = True
        self.fields['patient_balance'].widget.attrs['readonly'] = True

        self.fields['total_amount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_amount_to_pay_insurance'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_amount_to_pay_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['total_amount_paid_by_patient'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['patient_balance'].widget.attrs.update({'style': 'text-align: right;'})

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient


class ConsultationSheetSalePaymentForm(forms.ModelForm):
    amount = forms.CharField(
        label=_('Amount'),
    )
    currency = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = ConsultationSheetSalePayment
        fields = [
            'payment_datetime',
            'amount',
            'payment_method',
            'observations',
            'currency'
        ]

    def __init__(self, *args, **kwargs):
        super(ConsultationSheetSalePaymentForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['payment_datetime'].widget.attrs['class'] = 'payment_datetime'
        self.fields['payment_method'].widget.attrs['class'] = 'sale_payment_method'
        self.fields['amount'].widget.attrs['class'] = 'payment_amount'
        self.fields['observations'].widget.attrs['class'] = 'payment_observations'
        self.fields['currency'].widget.attrs['class'] = 'payment_currency'

    def clean_currency(self):
        currency_id = self.data['currency']
        currency = Currency.objects.get(pk=currency_id)
        return currency


ConsultationSheetSalePaymentFormSet = inlineformset_factory(
    ConsultationSheet, ConsultationSheetSalePayment, ConsultationSheetSalePaymentForm,
    extra=1,
)


class TechnicianConsultationCreateForm(forms.ModelForm):
    consultation_sheet = forms.CharField(widget=forms.HiddenInput())
    technician = forms.ModelChoiceField(
        queryset=Technician.objects.all(),
        required=True,
        label=_('Technician')
    )
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
                'readonly': True
            })
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Consultation
        fields = [
            'consultation_date',
            'technician',
            'patient',
            'medical_study',
            'medical_equipment',
            'treating_doctor',
            'notes',
            'consultation_sheet'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('consultation_sheet', type="hidden"),
                Div(
                    Row(
                        Column('consultation_date', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('technician', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('patient', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('medical_study', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('medical_equipment', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('treating_doctor', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('notes', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),

            ),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn-sm btn-primary shadow-sm'),
                HTML('<a class="btn btn-sm btn-light shadow-sm" href="'
                     + reverse('consultation_sheet.list_unrealized_technicians') + '">Cancelar</a>'),
                css_class='mx-auto'
            )
        )

        self.fields['medical_study'].widget.attrs['disabled'] = True
        self.fields['treating_doctor'].widget.attrs['disabled'] = True

    def clean_consultation_sheet(self):
        consultation_sheet_id = self.data['consultation_sheet']
        consultation_sheet = ConsultationSheet.objects.get(pk=consultation_sheet_id)
        return consultation_sheet

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient


class TechnicianConsultationUpdateForm(forms.ModelForm):
    consultation_sheet = forms.CharField(widget=forms.HiddenInput())
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
                'readonly': True
            })
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Consultation
        fields = [
            'consultation_date',
            'technician',
            'patient',
            'medical_study',
            'medical_equipment',
            'treating_doctor',
            'notes',
            'consultation_sheet'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('consultation_sheet', type="hidden"),
                Div(
                    Row(
                        Column('consultation_date', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('technician', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('patient', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('medical_study', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('medical_equipment', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('treating_doctor', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('notes', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),

            ),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn-sm btn-primary shadow-sm'),
                HTML('<a class="btn btn-sm btn-light shadow-sm" href="'
                     + reverse('consultation.list_technicians') + '">Cancelar</a>'),
                css_class='mx-auto'
            )
        )

        self.fields['medical_study'].widget.attrs['disabled'] = True
        self.fields['medical_equipment'].widget.attrs['disabled'] = True
        self.fields['treating_doctor'].widget.attrs['disabled'] = True

    def clean_consultation_sheet(self):
        consultation_sheet_id = self.data['consultation_sheet']
        consultation_sheet = ConsultationSheet.objects.get(pk=consultation_sheet_id)
        return consultation_sheet

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient


class DoctorConsultationCreateForm(forms.ModelForm):
    consultation_sheet = forms.CharField(widget=forms.HiddenInput())
    report_title = forms.CharField(
        required=True,
        label=_('Report Title')
    )
    template = forms.ModelChoiceField(
        required=False,
        label=_('Template'),
        queryset=DoctorReportTemplate.objects.all()
    )
    add_digital_signature = forms.BooleanField(
        label=_('Add Digital Signature'),
        required=False
    )
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
                'readonly': True
            })
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Consultation
        fields = [
            'consultation_date',
            'doctor',
            'patient',
            'medical_study',
            'treating_doctor',
            'notes',
            'consultation_sheet'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('consultation_sheet', type="hidden"),
                Div(
                    Row(
                        Column('consultation_date', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('doctor', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('patient', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('medical_study', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('treating_doctor', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('notes', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),

            ),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn-sm btn-primary shadow-sm'),
                HTML('<a class="btn btn-sm btn-light shadow-sm" href="'
                     + reverse('consultation_sheet.list_unrealized_doctors') + '">Cancelar</a>'),
                css_class='mx-auto'
            )
        )

        self.fields['medical_study'].widget.attrs['disabled'] = True
        self.fields['treating_doctor'].widget.attrs['disabled'] = True

    def clean_consultation_sheet(self):
        consultation_sheet_id = self.data['consultation_sheet']
        consultation_sheet = ConsultationSheet.objects.get(pk=consultation_sheet_id)
        return consultation_sheet

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient


class DoctorConsultationUpdateForm(forms.ModelForm):
    consultation_sheet = forms.CharField(widget=forms.HiddenInput())
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
                'readonly': True
            })
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Consultation
        fields = [
            'consultation_date',
            'doctor',
            'patient',
            'medical_study',
            'treating_doctor',
            'notes',
            'consultation_sheet'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('consultation_sheet', type="hidden"),
                Div(
                    Row(
                        Column('consultation_date', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('doctor', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('patient', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('medical_study', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('treating_doctor', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('notes', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),

            ),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn-sm btn-primary shadow-sm'),
                HTML('<a class="btn btn-sm btn-light shadow-sm" href="'
                     + reverse('consultation.list_doctors') + '">Cancelar</a>'),
                css_class='mx-auto'
            )
        )

        self.fields['doctor'].widget.attrs['disabled'] = True
        self.fields['medical_study'].widget.attrs['disabled'] = True
        self.fields['treating_doctor'].widget.attrs['disabled'] = True
        self.fields['consultation_date'].widget.attrs['disabled'] = True

    def clean_consultation_sheet(self):
        consultation_sheet_id = self.data['consultation_sheet']
        consultation_sheet = ConsultationSheet.objects.get(pk=consultation_sheet_id)
        return consultation_sheet

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient


class DoctorConsultationReportCreateForm(forms.ModelForm):
    consultations = forms.CharField(widget=forms.HiddenInput())
    template = forms.ModelChoiceField(
        required=False,
        label=_('Template'),
        queryset=DoctorReportTemplate.objects.all()
    )
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
                'readonly': True
            })
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = ConsultationReport
        fields = [
            'report_date',
            'doctor',
            'patient',
            'report_title',
            'add_digital_signature',
            'report',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('consultations', type="hidden"),
                Div(
                    Row(
                        Column('report_date', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('doctor', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('patient', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('report_title', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('report', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn-sm btn-primary shadow-sm'),
                HTML('<a class="btn btn-sm btn-light shadow-sm" href="'
                     + reverse('consultation.doctors_list_to_inform') + '">Cancelar</a>'),
                css_class='mx-auto'
            )
        )

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient


class ConsultationReportUpdateForm(forms.ModelForm):
    template = forms.ModelChoiceField(
        required=False,
        label=_('Template'),
        queryset=DoctorReportTemplate.objects.all()
    )
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Escriba aquí el nombre o CI del paciente',
                'readonly': True
            })
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = ConsultationReport
        fields = [
            'report_date',
            'doctor',
            'patient',
            'report_title',
            'add_digital_signature',
            'report',
            'finished'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Row(
                        Column('report_date', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('doctor', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('patient', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('report_title', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('report', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),

            ),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn-sm btn-primary shadow-sm'),
                HTML(
                    '<a class="btn btn-sm btn-light shadow-sm" href="' + reverse('consultation_report.list')
                    + '">Cancelar</a>'),
                css_class='mx-auto'
            )
        )

        self.fields['report_date'].widget.attrs['disabled'] = True
        self.fields['doctor'].widget.attrs['disabled'] = True

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient


class DoctorMultipleConsultationCreateForm(forms.Form):
    consultation_date = forms.DateTimeField(
        label=_('Consultation Date'),
        required=True,
    )
    doctor = forms.ModelChoiceField(
        label=_('Doctor'),
        queryset=Doctor.objects.all(),
        required=True
    )
    patient = forms.ModelChoiceField(
        label=_('Patient'),
        queryset=Patient.objects.all(),
        required=True
    )
    report_title = forms.CharField(
        label=_('Report Title'),
        required=True
    )
    template = forms.ModelChoiceField(
        required=False,
        label=_('Template'),
        queryset=DoctorReportTemplate.objects.all()
    )
    add_digital_signature = forms.BooleanField(
        required=False,
        label=_('Add Digital Signature')
    )
    report = forms.CharField(
        label=_('Report'),
        required=True,
        widget=CKEditorWidget
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Row(
                        Column('consultation_date', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('doctor', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('patient', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('report_title', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column('report', css_class='form-group col-md-12 '),
                        css_class='form-row '
                    ),
                    css_class=' mt-3 pl-3'
                ),

            ),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn-sm btn-primary shadow-sm'),
                HTML(
                    '<a class="btn btn-sm btn-light shadow-sm" href="'
                    + reverse('consultation_sheet.list_unrealized_doctors') + '">Cancelar</a>'),
                css_class='mx-auto'
            )
        )
        self.fields['patient'].widget.attrs['disabled'] = True


class ConsultationAssignFilesForm(forms.Form):
    consultation = forms.CharField(widget=forms.HiddenInput())
    doctor = forms.ModelChoiceField(
        label=_('Doctor'),
        required=True,
        queryset=Doctor.objects.all()
    )


class ConsultationFileForm(forms.ModelForm):
    consultation = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = ConsultationFile
        fields = [
            'file_name',
            'consultation',
            'consultation_file_type',
            'file',
        ]


ConsultationFileFormSet = inlineformset_factory(
    Consultation, ConsultationFile, ConsultationFileForm,
    fields=('file_name', 'consultation_file_type', 'file'),
    extra=1,
)