from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ConsultationConfig(AppConfig):
    name = 'consultation'
    verbose_name = _('Consultation')
