from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from base.models import Currency, Person
from clinic.models import MedicalStudy, MedicalEquipment, Doctor, Patient, Sector, TreatingDoctor, InsurancePlan
from scheduling.models import Appointment, AppointmentState, AppointmentDocument
from django.utils.translation import ugettext_lazy as _


class CalendarFiltersForm(forms.Form):
    date_filter = forms.CharField(
        label=_('Date Filter'),
        required=False,
    )
    # study_filter = forms.ModelChoiceField(
    #     label=_('Study filter'),
    #     required=False,
    #     queryset=MedicalStudy.objects.all()
    # )
    equipment_filter = forms.ModelChoiceField(
        label=_('Equipment filter'),
        required=False,
        queryset=MedicalEquipment.objects.all().exclude(sector__sector_code='ECO')
    )
    doctor_filter = forms.ModelChoiceField(
        label=_('Doctor filter'),
        required=False,
        queryset=Doctor.objects.filter(sectors__sector_code='ECO')
    )

    def __init__(self, *args, **kwargs):
        super(CalendarFiltersForm, self).__init__(*args, **kwargs)
        self.fields['date_filter'].label = False


class AppointmentDocumentForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'data-height': '200', 'data-default-file': ''}),
        label=_('File')
    )

    class Meta:
        model = AppointmentDocument
        fields = [
            'document_type',
            'file',
        ]

    def __init__(self, *args, **kwargs):
        super(AppointmentDocumentForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['class'] = 'dropify'


AppointmentDocumentFormSet = inlineformset_factory(
    Appointment, AppointmentDocument, AppointmentDocumentForm,
    fields=('document_type', 'file'),
    extra=1,
)


class AppointmentCreateForm(forms.ModelForm):
    MALE_CODE = 0
    FEMALE_CODE = 1

    SEX_CODES = (
        (MALE_CODE, _('Male')),
        (FEMALE_CODE, _('Female')),
    )

    appointment_state = forms.CharField(widget=forms.HiddenInput())
    currency = forms.CharField(widget=forms.HiddenInput())
    estimated_cost = forms.CharField(
        label=_('Estimated Cost'),
        required=False,
    )
    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Escriba aquí el nombre o CI del paciente'})
    )
    patient = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    medical_study_autocomplete = forms.CharField(
        label=_('Medical Study'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Escriba aquí el nombre del estudio'})
    )
    medical_study = forms.CharField(
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
    # Invoicing
    patient_address = forms.CharField(
        required=True,
        label=_('Address'),
    )
    patient_tax_id_number = forms.CharField(
        label=_('Patient Tax Id Number'),
        required=False,
    )
    patient_tax_id_name = forms.CharField(
        label=_('Patient Tax Id Name'),
        required=False,
    )
    patient_is_taxpayer = forms.BooleanField(
        label=_('Patient Is Taxpayer'),
        required=False,
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

    class Meta:
        model = Appointment
        fields = [
            'appointment_date_start',
            'appointment_date_end',
            'patient',
            'contact_number',
            'contact_email',
            'insurance_plan',
            'medical_study',
            'medical_equipment',
            'doctor',
            'appointment_state',
            'estimated_cost',
            'currency',
            'treating_doctor',
            'observations',
        ]

    def __init__(self, *args, **kwargs):
        super(AppointmentCreateForm, self).__init__(*args, **kwargs)
        self.fields['estimated_cost'].widget.attrs.update({'style': 'text-align: right;'})
        self.fields['medical_equipment'].widget.attrs.update({'data-placeholder': 'Elija una opción'})
        self.fields['doctor'].widget.attrs.update({'data-placeholder': 'Elija una opción'})

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

    def clean_appointment_state(self):
        appointment_state_name = self.data['appointment_state']
        appointment_state = AppointmentState.objects.get(name=appointment_state_name)
        return appointment_state

    def clean_currency(self):
        currency_name = self.data['currency']
        currency = Currency.objects.get(name=currency_name)
        return currency

    def clean_patient(self):
        patient_id = self.data['patient']
        if patient_id != '':
            patient = Patient.objects.get(pk=patient_id)
        else:
            patient = None
        return patient

    def clean_patient_document_number(self):
        patient_document_number = self.data['patient_document_number']
        if "new_patient" in self.data:
            new_patient = True
        else:
            new_patient = False

        existing_patient = Patient.objects.filter(document_number=patient_document_number)
        if existing_patient and new_patient:
            raise ValidationError(_("A patient with this document number already exist!"))
        return patient_document_number

    def clean_medical_study(self):
        medical_study_id = self.data['medical_study']
        medical_study = MedicalStudy.objects.get(pk=medical_study_id)
        return medical_study

    def clean_medical_equipment(self):

        medical_equipment_id = self.data['medical_equipment']
        doctor_id = self.data['doctor']

        # validacion
        if medical_equipment_id == '':
            if doctor_id == '':
                raise ValidationError(_("Debe ingresar equipo medico o doctor"))
            return None
        else:
            medical_equipment = MedicalEquipment.objects.get(pk=medical_equipment_id)
            return medical_equipment


class AppointmentUpdateForm(forms.ModelForm):
    appointment_state = forms.CharField(widget=forms.HiddenInput())
    currency = forms.CharField(widget=forms.HiddenInput())
    estimated_cost = forms.CharField(
        label=_('Estimated Cost'),
        required=False
    )

    patient_autocomplete = forms.CharField(
        label=_('Patient'),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Escriba aquí el nombre o CI del paciente'})
    )
    patient = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    medical_study_autocomplete = forms.CharField(
        label=_('Medical Study'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Escriba aquí el nombre del estudio'})
    )
    medical_study = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    # Invoicing
    patient_address = forms.CharField(
        required=True,
        label=_('Address'),
    )
    patient_tax_id_number = forms.CharField(
        label=_('Patient Tax Id Number'),
        required=False,
    )
    patient_tax_id_name = forms.CharField(
        label=_('Patient Tax Id Name'),
        required=False,
    )
    patient_is_taxpayer = forms.BooleanField(
        label=_('Patient Is Taxpayer'),
        required=False,
    )

    class Meta:
        model = Appointment
        fields = [
            'appointment_date_start',
            'appointment_date_end',
            'patient',
            # Invoicing
            'contact_number',
            'contact_email',

            'insurance_plan',
            'medical_study',
            'medical_equipment',
            'doctor',
            'appointment_state',
            'estimated_cost',
            'currency',
            'treating_doctor',
            'observations'
        ]

    def __init__(self, *args, **kwargs):
        super(AppointmentUpdateForm, self).__init__(*args, **kwargs)
        self.fields['estimated_cost'].widget.attrs.update({'style': 'text-align: right;'})

        self.fields['contact_email'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['contact_email'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['observations'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['observations'].widget.attrs.update({'class': 'to-upper-case'})

    def clean_appointment_state(self):
        appointment_state_id = self.data['appointment_state']
        appointment_state = AppointmentState.objects.get(pk=appointment_state_id)
        return appointment_state

    def clean_currency(self):
        currency_id = self.data['currency']
        currency = Currency.objects.get(pk=currency_id)
        return currency

    def clean_patient(self):
        patient_id = self.data['patient']
        patient = Patient.objects.get(pk=patient_id)
        return patient

    def clean_medical_study(self):
        medical_study_id = self.data['medical_study']
        medical_study = MedicalStudy.objects.get(pk=medical_study_id)
        return medical_study


class AppointmentReportFiltersForm(forms.Form):
    HTML_TYPE = 1
    EXCEL_TYPE = 2
    PDF_TYPE = 3

    REPORTS_TYPES = (
        (HTML_TYPE, _('Web')),
        (EXCEL_TYPE, _('Excel')),
        (PDF_TYPE, _('Pdf')),
    )

    date_time_start = forms.DateTimeField(
        label=_('Date Time Start Filter'),
        required=False,
    )
    date_time_end = forms.DateTimeField(
        label=_('Date Time End Filter'),
        required=False,
    )
    insurance_plan = forms.ModelChoiceField(
        queryset=InsurancePlan.objects.all(),
        label=_('Insurance Plan'),
        required=False
    )
    medical_study = forms.ModelChoiceField(
        label=_('Medical Study'),
        queryset=MedicalStudy.objects.all(),
        required=False
    )
    medical_equipment = forms.ModelChoiceField(
        label=_('Medical Equipment'),
        queryset=MedicalEquipment.objects.all(),
        required=False
    )
    doctor = forms.ModelChoiceField(
        label=_('Doctor'),
        queryset=Doctor.objects.all(),
        required=False
    )
    treating_doctor = forms.ModelChoiceField(
        label=_('Treating Doctor'),
        queryset=TreatingDoctor.objects.all(),
        required=False
    )
    appointment_state = forms.ModelChoiceField(
        label=_('Appointment State'),
        queryset=AppointmentState.objects.all(),
        required=False
    )
    sector = forms.ModelChoiceField(
        label=_('Sector'),
        required=False,
        queryset=Sector.objects.all()
    )
    user = forms.ModelChoiceField(
        label=_('User who scheduled'),
        required=False,
        queryset=User.objects.all()
    )

    user = forms.ModelChoiceField(
        label=_('User who scheduled'),
        required=False,
        queryset=User.objects.all()
    )

    user = forms.ModelChoiceField(
        label=_('User who scheduled'),
        required=False,
        queryset=User.objects.all()
    )

    report_type = forms.ChoiceField(
        label=_('Report Type'),
        choices=REPORTS_TYPES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(AppointmentReportFiltersForm, self).__init__(*args, **kwargs)


class AppointmentsOfTheDayReportFiltersForm(forms.Form):
    HTML_TYPE = 1
    EXCEL_TYPE = 2
    PDF_TYPE = 3

    FIFTEEN_MIN_TYPE = 15
    TWENTY_MIN_TYPE = 20
    THIRTY_MIN_TYPE = 30

    REPORTS_TYPES = (
        (HTML_TYPE, _('Web')),
        # (EXCEL_TYPE, _('Excel')),
        (PDF_TYPE, _('Pdf')),
    )

    TIME_INTERVAL_TYPES = (
        (FIFTEEN_MIN_TYPE, '15 min'),
        (TWENTY_MIN_TYPE, '20 min'),
        (THIRTY_MIN_TYPE, '30 min'),
    )

    date = forms.DateTimeField(
        label=_('Date'),
        required=True,
    )

    medical_equipment = forms.ModelChoiceField(
        label=_('Medical Equipment'),
        queryset=MedicalEquipment.objects.all(),
        required=False
    )
    doctor = forms.ModelChoiceField(
        label=_('Doctor'),
        queryset=Doctor.objects.all(),
        required=False
    )
    time_interval = forms.ChoiceField(
        label=_('Time Interval'),
        choices=TIME_INTERVAL_TYPES,
        required=False
    )

    report_type = forms.ChoiceField(
        label=_('Report Type'),
        choices=REPORTS_TYPES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(AppointmentsOfTheDayReportFiltersForm, self).__init__(*args, **kwargs)
