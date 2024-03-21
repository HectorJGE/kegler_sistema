from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SalesConfig(AppConfig):
    name = 'sales'
    verbose_name = _('Sales')