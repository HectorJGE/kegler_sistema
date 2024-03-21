import datetime
from django import template
from django.template.defaultfilters import stringfilter
from django.utils import timezone
from django.utils.dateparse import parse_datetime
import locale
register = template.Library()


@register.filter
@stringfilter
def datedate(value, format="%d/%m/%Y %H:%M"):
    locale.setlocale(locale.LC_TIME, "es")
    try:
        print(value)
        my_date = parse_datetime(value)
        my_date = my_date + datetime.timedelta(hours=-4)
        my_date = timezone.make_aware(my_date)
        my_date_str = my_date.strftime(format)
        return my_date_str
    except Exception as e:
        print(e)
        return ""
