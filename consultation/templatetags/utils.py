import locale

import datetime
from django import template
import unicodedata

from django.template.defaultfilters import stringfilter
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from pytz import unicode

register = template.Library()


@register.filter(name='stripaccents')
def stripaccents(text, arg=""):
    try:
        text = unicode(text, 'utf-8')
    except:  # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text) \
        .encode('ascii', 'ignore') \
        .decode("utf-8")
    return str(text)


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
@stringfilter
def datedate(value, format="%d/%m/%Y %H:%M"):
    # locale.setlocale(locale.LC_TIME, "es")
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
