from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'autofocus': "true",
            'placeholder': _('Enter Username'),
            'class': 'form-control form-control-user',
            'aria-describedby': "emailHelp",
            'id': 'exampleInputEmail',
        }),
        error_messages={'required': _('Please enter your account username')}
    )

    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': _('Password'),
            'class': 'form-control form-control-user',
            'id': 'exampleInputPassword',
        }),
        error_messages={'required': _('Must enter your password')}
    )