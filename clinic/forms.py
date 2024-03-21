from django import forms
from django.utils.translation import ugettext_lazy as _

from base.models import Person
from clinic.models import Patient


class PatientForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=True,
        label=_('Phone Number')
    )
    weight = forms.CharField(
        required=True,
        label=_('Weight')
    )
    birth_date = forms.DateField(
        required=True,
        label=_('Birth Date'),
        widget=forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa'}),
    )
    city = forms.ChoiceField(
        required=True,
        label=_('City'),
        choices=Person.CITYS
    )
    address = forms.CharField(
        required=True,
        label=_('address'),
    )

    class Meta:
        model = Patient
        fields = [
            'name',
            'last_name',
            'sex',
            'weight',
            'document_number',

            # invoicing
            'tax_identification_number',
            'tax_identification_name',
            'email',
            'address',
            'phone_number',
            'is_taxpayer',

            'birth_date',
            'city',
            'insurance_plan'
        ]

    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['name'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['last_name'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['last_name'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['address'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['address'].widget.attrs.update({'class': 'to-upper-case'})

        self.fields['email'].widget.attrs.update({'style': 'text-transform: uppercase'})
        self.fields['email'].widget.attrs.update({'class': 'to-upper-case'})

