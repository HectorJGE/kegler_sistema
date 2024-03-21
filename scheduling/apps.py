from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SchedulingConfig(AppConfig):
    name = 'scheduling'
    verbose_name = _('Scheduling')
