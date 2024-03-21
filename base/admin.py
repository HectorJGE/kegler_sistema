from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from base.models import Currency, UserPrintTagConfiguration


# Register your models here.
# ########################### CURRENCY
class CurrencyResource(resources.ModelResource):

    class Meta:
        model = Currency


class CurrencyAdmin(ImportExportModelAdmin):
    resource_class = CurrencyResource
    search_fields = ['id', 'name', 'code', 'sufix']
    list_filter = ['created_at', 'updated_at']
    list_display = ('id', 'name', 'code', 'sufix',
                    'created_at',
                    'updated_at')


admin.site.register(Currency, CurrencyAdmin)


# ########################### USER PRINT TAG CONFIGURATION
class UserPrintTagConfigurationResource(resources.ModelResource):

    class Meta:
        model = UserPrintTagConfiguration


class UserPrintTagConfigurationAdmin(ImportExportModelAdmin):
    resource_class = UserPrintTagConfigurationResource
    search_fields = ['id', 'user__username']
    list_filter = ['user', 'created_at', 'updated_at']
    list_display = ('id', 'user', 'name_x', 'name_y',
                    'last_name_x', 'last_name_y', 'date_x', 'date_y',
                    'created_at',
                    'updated_at')


admin.site.register(UserPrintTagConfiguration, UserPrintTagConfigurationAdmin)
