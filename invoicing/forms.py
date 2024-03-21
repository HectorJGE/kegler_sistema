from datetime import datetime

from django import forms
from django.forms import ModelForm, inlineformset_factory
from .models import *
from crispy_forms.layout import Layout, Fieldset, Div, Row, Column, Field
from crispy_forms.helper import FormHelper
from django.utils.translation import ugettext_lazy as _

CONDITIONS = (
    ('CONTADO', 'CONTADO'),
    ('CREDITO', 'CREDITO'),
)


# Invoice Creation form
class InvoiceHeaderForm(ModelForm):
    payment_term = forms.ChoiceField(choices=CONDITIONS,
                                     widget=forms.Select,
                                     initial='CONTADO',
                                     label=_('Payment Term'))
    company = forms.ChoiceField(widget=forms.Select,
                                label=_('Issuing Company')
                                )

    invoice_date = forms.DateField(
        required=True,
        label=_('Invoice Date'),
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'}),
    )
    currency = forms.ModelChoiceField(queryset=Currency.objects.all(),
                                      widget=forms.HiddenInput(),
                                      initial=Currency.objects.first(), )
    invoice_stamp = forms.CharField(widget=forms.HiddenInput())
    customer = forms.CharField(widget=forms.HiddenInput(), required=False)
    subtotal = forms.CharField(label=_('Sub Total'))
    total_exempt = forms.CharField(label=_('Total Exempt'))
    invoice_total = forms.CharField(label=_('Invoice Total'))
    total_tax10 = forms.CharField(label=_('Total TAX 10%'))
    total_tax5 = forms.CharField(label=_('Total TAX 5%'))
    total_tax = forms.CharField(label=_('Total TAX'))
    client_tax_payer = forms.BooleanField(label=_('Is Tax Payer'), initial=True, required=False)

    class Meta:
        model = InvoiceHeader
        fields = [
            'company',
            'customer',
            'invoice_number',
            'invoice_stamp',
            'client_name',
            'client_tax_identification_number',
            'client_email',
            'client_address',
            'client_phone_number',
            'invoice_date',
            'payment_term',
            'subtotal',
            'invoice_total',
            'total_tax10',
            'total_tax5',
            'total_exempt',
            'total_tax',
            'currency',
            'invoice_total_letters'
        ]

    def clean_invoice_stamp(self):
        invoice_stamp_id = self.data['invoice_stamp']
        invoice_stamp = InvoiceStamp.objects.get(pk=invoice_stamp_id)
        return invoice_stamp

    def clean_customer(self):
        customer_id = self.data['customer']
        if customer_id != '':
            customer = Customer.objects.filter(pk=customer_id).first()
        else:
            customer = None

        return customer

    def get_companies(self):
        user = self.user
        choices = []

        if user.is_superuser:
            companies_user = IssuingCompanyName.objects.all()
        else:
            stamp_ranges = StampRange.objects.filter(user=user)
            issuing_company_names = stamp_ranges.values_list('stamp__company_name__company_name', flat=True).distinct()
            companies_user = IssuingCompanyName.objects.filter(company_name__in=issuing_company_names)

        for company in companies_user:
            choices.append((company.company_name, company.company_name))

        return choices

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['invoice_date'].input_formats = ['%d/%m/%Y']
        self.fields['invoice_date'].widget.attrs['readonly'] = True
        self.fields['company'].choices = self.get_companies()
        self.fields['total_exempt'].widget.attrs['readonly'] = True
        self.fields['total_tax5'].widget.attrs['readonly'] = True
        self.fields['total_tax10'].widget.attrs['readonly'] = True
        self.fields['total_tax'].widget.attrs['readonly'] = True
        self.fields['subtotal'].widget.attrs['readonly'] = True
        self.fields['invoice_total'].widget.attrs['readonly'] = True
        self.fields['invoice_total_letters'].widget.attrs['readonly'] = True


class InvoiceDetailsForm(ModelForm):
    quantity = forms.CharField(label=_('Quantity'))
    unit_price = forms.CharField(label=_('Unit Price'))
    exempt = forms.CharField(label=_('Exempt'))
    tax_5 = forms.CharField(label=_('TAX 5%'))
    tax_10 = forms.CharField(label=_('TAX 10%'))

    class Meta:
        model = InvoiceDetails
        fields = [
            'invoice_header',
            'quantity',
            'description',
            'unit_price',
            'exempt',
            'tax_5',
            'tax_10'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs['class'] = 'quantity'
        self.fields['description'].widget.attrs['class'] = 'description'
        self.fields['unit_price'].widget.attrs['class'] = 'unit_price'
        self.fields['tax_5'].widget.attrs['class'] = 'tax_5'
        self.fields['tax_10'].widget.attrs['class'] = 'tax_10'
        self.fields['exempt'].widget.attrs['class'] = 'exempt'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.attrs = {
            'novalidate': ''
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('invoice_header', type="hidden"),
                Div(
                    Row(
                        Column(
                            Field('quantity', css_id='quantity'),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('description', css_id='description'),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('unit_price', css_id='unit_price'),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('tax_10', css_id="tax_10"),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('tax_5', css_id="tax_5"),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('exempt', css_id="exempt"),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
            )
        )


InvoiceDetailsFormSet = inlineformset_factory(
    InvoiceHeader, InvoiceDetails, InvoiceDetailsForm,
    extra=1,
    can_delete=True,
)


# Creation form
class InvoiceUpdateForm(ModelForm):
    payment_term = forms.ChoiceField(choices=CONDITIONS,
                                     widget=forms.Select,
                                     initial='CONTADO',
                                     label=_('Payment Term'))
    company = forms.ModelChoiceField(
        queryset=IssuingCompanyName.objects.all(),
        widget=forms.Select,
        disabled=True,
    )
    invoice_date = forms.DateField(
        required=True,
        label=_('Invoice Date'),
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'}),
    )
    currency = forms.ModelChoiceField(queryset=Currency.objects.all(),
                                      widget=forms.HiddenInput(),
                                      initial=Currency.objects.first(), )
    invoice_stamp = forms.CharField(widget=forms.HiddenInput())
    customer = forms.CharField(widget=forms.HiddenInput(), required=False)
    subtotal = forms.CharField(label=_('Sub Total'))
    total_exempt = forms.CharField(label=_('Total Exempt'))
    invoice_total = forms.CharField(label=_('Invoice Total'))
    total_tax10 = forms.CharField(label=_('Total TAX 10%'))
    total_tax5 = forms.CharField(label=_('Total TAX 5%'))
    total_tax = forms.CharField(label=_('Total TAX'))
    client_tax_payer = forms.BooleanField(label=_('Is Tax Payer'), required=False)

    class Meta:
        model = InvoiceHeader
        fields = [
            'company',
            'customer',
            'invoice_number',
            'invoice_stamp',
            'client_name',
            'client_email',
            'client_address',
            'client_phone_number',
            'client_tax_identification_number',
            'invoice_date',
            'payment_term',
            'subtotal',
            'invoice_total',
            'total_exempt',
            'total_tax10',
            'total_tax5',
            'total_tax',
            'currency',
            'invoice_total_letters'
        ]

    def clean_invoice_stamp(self):
        invoice_stamp_id = self.data['invoice_stamp']
        invoice_stamp = InvoiceStamp.objects.get(pk=invoice_stamp_id)
        return invoice_stamp

    def clean_customer(self):
        customer_id = self.data['customer']
        if customer_id != '':
            customer = Customer.objects.filter(pk=customer_id).first()
        else:
            customer = None

        return customer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invoice_date'].input_formats = ['%d/%m/%Y']
        self.fields['company'].initial = IssuingCompanyName.objects.first()
        self.fields['total_exempt'].widget.attrs['readonly'] = True
        self.fields['total_tax5'].widget.attrs['readonly'] = True
        self.fields['total_tax10'].widget.attrs['readonly'] = True
        self.fields['total_tax'].widget.attrs['readonly'] = True
        self.fields['subtotal'].widget.attrs['readonly'] = True
        self.fields['invoice_total'].widget.attrs['readonly'] = True
        self.fields['invoice_total_letters'].widget.attrs['readonly'] = True


# Credit Note Creation form
class CreditNoteHeaderCreateForm(ModelForm):
    invoice_header = forms.ModelChoiceField(
        queryset=InvoiceHeader.objects.all(),
        widget=forms.Select,
        label=_('Invoice Header')
    )
    company = forms.ModelChoiceField(
        queryset=IssuingCompanyName.objects.all(),
        widget=forms.Select,
        label=_('Issuing Company')
    )
    credit_note_date = forms.DateField(
        required=True,
        label=_('Credit Note Date'),
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'}),
    )
    currency = forms.ModelChoiceField(queryset=Currency.objects.all(),
                                      widget=forms.HiddenInput(),
                                      initial=Currency.objects.first(), )
    credit_note_stamp = forms.CharField(widget=forms.HiddenInput())
    customer = forms.CharField(widget=forms.HiddenInput(), required=False)
    subtotal = forms.CharField(label=_('Sub Total'))
    total_exempt = forms.CharField(label=_('Total Exempt'))
    credit_note_total = forms.CharField(label=_('Invoice Total'))
    total_tax10 = forms.CharField(label=_('Total TAX 10%'))
    total_tax5 = forms.CharField(label=_('Total TAX 5%'))
    total_tax = forms.CharField(label=_('Total TAX'))
    client_tax_payer = forms.BooleanField(label=_('Is Tax Payer'), required=False)

    class Meta:
        model = CreditNoteHeader
        fields = [
            'company',
            'invoice_header',
            'customer',
            'credit_note_number',
            'credit_note_stamp',
            'client_name',
            'client_tax_identification_number',
            'client_email',
            'client_address',
            'client_phone_number',
            'client_tax_payer',
            'credit_note_date',
            'subtotal',
            'credit_note_total',
            'total_exempt',
            'total_tax10',
            'total_tax5',
            'total_tax',
            'currency',
            'credit_note_total_letters'
        ]

    def clean_credit_note_stamp(self):
        credit_note_stamp_id = self.data['credit_note_stamp']
        credit_note_stamp = CreditNoteStamp.objects.get(pk=credit_note_stamp_id)
        return credit_note_stamp

    def clean_credit_note_total(self):
        invoice_header = self.cleaned_data.get('invoice_header')
        credit_note_total = self.cleaned_data.get('credit_note_total')

        credit_notes_total = 0.0
        for credit_note in invoice_header.credit_notes.all():
            credit_notes_total += credit_note.credit_note_total

        if invoice_header.invoice_total < (credit_notes_total + float(credit_note_total)):
            raise forms.ValidationError("El valor de esta Nota de Crédito, sumado con el valor de las demás notas de "
                                        "crédito, supero el valor de la factura referida")

        return credit_note_total

    def clean_customer(self):
        customer_id = self.data['customer']
        if customer_id != '':
            customer = Customer.objects.filter(pk=customer_id).first()
        else:
            customer = None

        return customer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['credit_note_date'].input_formats = ['%d/%m/%Y']
        self.fields['credit_note_date'].widget.attrs['readonly'] = True
        self.fields['company'].initial = IssuingCompanyName.objects.first()
        self.fields['total_exempt'].widget.attrs['readonly'] = True
        self.fields['total_tax5'].widget.attrs['readonly'] = True
        self.fields['total_tax10'].widget.attrs['readonly'] = True
        self.fields['total_tax'].widget.attrs['readonly'] = True
        self.fields['subtotal'].widget.attrs['readonly'] = True
        self.fields['credit_note_total'].widget.attrs['readonly'] = True
        self.fields['credit_note_total_letters'].widget.attrs['readonly'] = True


class CreditNoteDetailForm(ModelForm):
    quantity = forms.CharField(label=_('Quantity'))
    unit_price = forms.CharField(label=_('Unit Price'))
    exempt = forms.CharField(label=_('Exempt'))
    tax_5 = forms.CharField(label=_('TAX 5%'))
    tax_10 = forms.CharField(label=_('TAX 10%'))

    class Meta:
        model = CreditNoteDetail
        fields = [
            'credit_note_header',
            'quantity',
            'description',
            'unit_price',
            'exempt',
            'tax_5',
            'tax_10'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs['class'] = 'quantity'
        self.fields['description'].widget.attrs['class'] = 'description'
        self.fields['unit_price'].widget.attrs['class'] = 'unit_price'
        self.fields['tax_5'].widget.attrs['class'] = 'tax_5'
        self.fields['tax_10'].widget.attrs['class'] = 'tax_10'
        self.fields['exempt'].widget.attrs['class'] = 'exempt'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.attrs = {
            'novalidate': ''
        }
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('credit_note_header', type="hidden"),
                Div(
                    Row(
                        Column(
                            Field('quantity', css_id='quantity'),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('description', css_id='description'),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('unit_price', css_id='unit_price'),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('tax_10', css_id="tax_10"),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('tax_5', css_id="tax_5"),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
                Div(
                    Row(
                        Column(
                            Field('exempt', css_id="exempt"),
                            css_class='form-group col-md-12'),
                        css_class='form-row'
                    ),
                    css_class='mt-3 pl-3'
                ),
            )
        )


CreditNoteDetailsFormSet = inlineformset_factory(
    CreditNoteHeader, CreditNoteDetail, CreditNoteDetailForm,
    extra=1,
    can_delete=True,
)


# Credit Note Update form
class CreditNoteHeaderUpdateForm(ModelForm):
    invoice_header = forms.ModelChoiceField(
        required=True,
        queryset=InvoiceHeader.objects.all(),
        widget=forms.Select,
        label=_('Invoice Header')
    )
    company = forms.ModelChoiceField(
        required=True,
        queryset=IssuingCompanyName.objects.all(),
        widget=forms.Select,
        label=_('Issuing Company')
    )
    credit_note_date = forms.DateField(
        required=True,
        label=_('Credit Note Date'),
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'dd/mm/aaaa'}),
    )
    currency = forms.ModelChoiceField(queryset=Currency.objects.all(),
                                      widget=forms.HiddenInput(),
                                      initial=Currency.objects.first(), )
    credit_note_stamp = forms.CharField(widget=forms.HiddenInput())
    customer = forms.CharField(widget=forms.HiddenInput(), required=False)
    subtotal = forms.CharField(label=_('Sub Total'))
    total_exempt = forms.CharField(label=_('Total Exempt'))
    credit_note_total = forms.CharField(label=_('Credit Note Total'))
    total_tax10 = forms.CharField(label=_('Total TAX 10%'))
    total_tax5 = forms.CharField(label=_('Total TAX 5%'))
    total_tax = forms.CharField(label=_('Total TAX'))
    client_tax_payer = forms.BooleanField(label=_('Is Tax Payer'), required=False)

    class Meta:
        model = CreditNoteHeader
        fields = [
            'company',
            'invoice_header',
            'customer',
            'credit_note_number',
            'credit_note_stamp',
            'client_name',
            'client_tax_identification_number',
            'client_email',
            'client_address',
            'client_phone_number',
            'client_tax_payer',
            'credit_note_date',
            'subtotal',
            'credit_note_total',
            'total_exempt',
            'total_tax10',
            'total_tax5',
            'total_tax',
            'currency',
            'credit_note_total_letters'
        ]

    def clean_credit_note_total(self):
        invoice_header = self.cleaned_data.get('invoice_header')
        credit_note_total = self.cleaned_data.get('credit_note_total')

        credit_notes_total = 0.0
        for credit_note in invoice_header.credit_notes.all():
            credit_notes_total += credit_note.credit_note_total

        if invoice_header.invoice_total < (credit_notes_total + float(credit_note_total)):
            raise forms.ValidationError("El valor de esta Nota de Crédito, sumado con el valor de las demás notas de "
                                        "crédito, supero el valor de la factura referida")

        return credit_note_total

    def clean_credit_note_stamp(self):
        credit_note_stamp_id = self.data['credit_note_stamp']
        credit_note_stamp = CreditNoteStamp.objects.get(pk=credit_note_stamp_id)
        return credit_note_stamp

    def clean_customer(self):
        customer_id = self.data['customer']
        if customer_id != '':
            customer = Customer.objects.filter(pk=customer_id).first()
        else:
            customer = None

        return customer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['credit_note_date'].input_formats = ['%d/%m/%Y']
        self.fields['company'].initial = IssuingCompanyName.objects.first()
        self.fields['total_exempt'].widget.attrs['readonly'] = True
        self.fields['total_tax5'].widget.attrs['readonly'] = True
        self.fields['total_tax10'].widget.attrs['readonly'] = True
        self.fields['total_tax'].widget.attrs['readonly'] = True
        self.fields['subtotal'].widget.attrs['readonly'] = True
        self.fields['credit_note_total'].widget.attrs['readonly'] = True
        self.fields['credit_note_total_letters'].widget.attrs['readonly'] = True


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = [
            'customer_name',
            'customer_tax_id_number',
            'customer_email',
            'customer_address',
            'customer_phone_number',
            'is_taxpayer',
            'customer_type',
            'sifen_ruc_validated',
            'patient'
        ]
