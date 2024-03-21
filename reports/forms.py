from django import forms
from clinic.models import Doctor, TreatingDoctor, InsurancePlan, Sector, MedicalStudyType, MedicalStudy, MedicalEquipment, Patient
from django.utils.translation import ugettext_lazy as _

from invoicing.models import PaymentMethod, IssuingCompanyName, Customer


class CashReportFiltersForm(forms.Form):
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
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(),
        label=_('Payment Method'),
        required=False
    )
    study_type = forms.ModelChoiceField(
        label=_('Medical Study Type'),
        queryset=MedicalStudyType.objects.all(),
        required=False
    )
    report_type = forms.ChoiceField(
        label=_('Report Type'),
        choices=REPORTS_TYPES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(CashReportFiltersForm, self).__init__(*args, **kwargs)


class InvoiceReportFiltersForm(forms.Form):
    HTML_TYPE = 1
    EXCEL_TYPE = 2
    ABACO_TYPE = 3

    REPORTS_TYPES = (
        (HTML_TYPE, _('Web')),
        (EXCEL_TYPE, _('Excel')),
        (ABACO_TYPE, _('Abaco')),
    )

    PAYMENT_TERM = (
        ('', '-------'),
        ('CONTADO', 'CONTADO'),
        ('CREDITO', 'CREDITO')
    )

    date_time_start = forms.DateField(
        label=_('Date Time Start Filter'),
        required=True,
    )
    date_time_end = forms.DateField(
        label=_('Date Time End Filter'),
        required=True,
    )
    company_name = forms.ModelChoiceField(
        queryset=IssuingCompanyName.objects.all(),
        label=_('Company Name'),
        required=False
    )
    client = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        label=_('Cliente'),
        required=False
    )
    payment_term = forms.ChoiceField(
        label=_('Payment Term'),
        choices=PAYMENT_TERM,
        required=False
    )
    report_type = forms.ChoiceField(
        label=_('Report Type'),
        choices=REPORTS_TYPES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(InvoiceReportFiltersForm, self).__init__(*args, **kwargs)


class ReportingDoctorsReportFiltersForm(forms.Form):
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
    reporting_doctor = forms.ModelChoiceField(
        label=_('Reporting Doctor'),
        required=False,
        queryset=Doctor.objects.all()
    )
    sector = forms.ModelChoiceField(
        label=_('Sector'),
        required=False,
        queryset=Sector.objects.all()
    )
    report_type = forms.ChoiceField(
        label=_('Report Type'),
        choices=REPORTS_TYPES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(ReportingDoctorsReportFiltersForm, self).__init__(*args, **kwargs)


class TreatingDoctorsReportFiltersForm(forms.Form):
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
    treating_doctor = forms.ModelChoiceField(
        label=_('Treating Doctor'),
        required=False,
        queryset=TreatingDoctor.objects.all()
    )
    sector = forms.ModelChoiceField(
        label=_('Sector'),
        required=False,
        queryset=Sector.objects.all()
    )
    report_type = forms.ChoiceField(
        label=_('Report Type'),
        choices=REPORTS_TYPES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(TreatingDoctorsReportFiltersForm, self).__init__(*args, **kwargs)


class InsurancesAgreementsReportFiltersForm(forms.Form):
    HTML_TYPE = 1
    EXCEL_TYPE = 2
    PDF_TYPE = 3

    INSURANCE_ENTRY_SHEETS_TO_PAY_WITHOUT_INVOICES = 1
    INSURANCE_ENTRY_SHEETS_TO_PAY_WITH_INVOICES = 2
    ALL_INSURANCE_ENTRY_SHEETS_TO_PAY = 3


    INVOICES_FILTER_CHOICES = (
        (INSURANCE_ENTRY_SHEETS_TO_PAY_WITHOUT_INVOICES, _('Insurance Entry Sheets To pay without Invoices')),
        (INSURANCE_ENTRY_SHEETS_TO_PAY_WITH_INVOICES, _('Insurance Entry Sheets To pay with Invoices')),
        (ALL_INSURANCE_ENTRY_SHEETS_TO_PAY, _('Al Insurance Entry Sheets To pay')),
    )

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
        label=_('Insurance Plan'),
        required=False,
        queryset=InsurancePlan.objects.all()
    )
    sector = forms.ModelChoiceField(
        label=_('Sector'),
        required=False,
        queryset=Sector.objects.all()
    )
    study_type = forms.ModelChoiceField(
        label=_('Medical Study Type'),
        queryset=MedicalStudyType.objects.all(),
        required=False
    )
    report_type = forms.ChoiceField(
        label=_('Report Type'),
        choices=REPORTS_TYPES,
        required=False
    )
    invoice_filter = forms.ChoiceField(
        label=_('Invoice Filter'),
        choices=INVOICES_FILTER_CHOICES,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(InsurancesAgreementsReportFiltersForm, self).__init__(*args, **kwargs)


class ConsultationSheetsTotalReportFiltersForm(forms.Form):
    HTML_TYPE = 1
    EXCEL_TYPE = 2
    PDF_TYPE = 3

    REPORTS_TYPES = (
        (HTML_TYPE, _('Web')),
        (EXCEL_TYPE, _('Excel')),
        # (PDF_TYPE, _('Pdf')),
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
        label=_('Insurance Plan'),
        required=False,
        queryset=InsurancePlan.objects.all()
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
    sector = forms.ModelChoiceField(
        label=_('Sector'),
        required=False,
        queryset=Sector.objects.all()
    )
    study_type = forms.ModelChoiceField(
        label=_('Medical Study Type'),
        queryset=MedicalStudyType.objects.all(),
        required=False
    )
    reporting_doctor = forms.ModelChoiceField(
        label=_('Reporting Doctor'),
        required=False,
        queryset=Doctor.objects.all()
    )
    treating_doctor = forms.ModelChoiceField(
        label=_('Treating Doctor'),
        required=False,
        queryset=TreatingDoctor.objects.all()
    )
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(),
        label=_('Payment Method'),
        required=False
    )
    report_type = forms.ChoiceField(
        label=_('Report Type'),
        choices=REPORTS_TYPES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(ConsultationSheetsTotalReportFiltersForm, self).__init__(*args, **kwargs)
