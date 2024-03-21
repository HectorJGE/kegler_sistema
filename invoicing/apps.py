from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class InvoicingConfig(AppConfig):
    name = 'invoicing'
    verbose_name = _('Invoicing')
