from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ClinicConfig(AppConfig):
    name = 'clinic'
    verbose_name = _('Clinic')

