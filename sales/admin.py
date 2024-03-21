from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from sales.models import ConsultationEntrySheetSaleHeader, ConsultationSheetSaleDetail, ConsultationSheetSalePayment


# Register your models here.

# Consultation Sheet Sale Detail Admin Inline
class ConsultationSheetSaleDetailAdminInlineAdmin(admin.TabularInline):
    model = ConsultationSheetSaleDetail


# Consultation Sheet Sale Payment Admin Inline
class ConsultationSheetSalePaymentAdminInlineAdmin(admin.TabularInline):
    model = ConsultationSheetSalePayment


# ############################### CONSULTATION ENTRY SHEET SALE HEADER
class ConsultationEntrySheetSaleHeaderResource(resources.ModelResource):

    class Meta:
        model = ConsultationEntrySheetSaleHeader


class ConsultationEntrySheetSaleHeaderAdmin(ImportExportModelAdmin):
    resource_class = ConsultationEntrySheetSaleHeaderResource
    search_fields = ['id',
                     'client_name',
                     'client_tax_identification_number',
                     'created_at', 'updated_at'
                     ]

    list_display = (
        'id',
        'client_name',
        'client_tax_identification_number',
        'sale_date',
        'sale_total',
        'currency',
        'consultation_entry_sheet',
        'created_at',
        'updated_at'
    )

    inlines = [
        ConsultationSheetSaleDetailAdminInlineAdmin,
        ConsultationSheetSalePaymentAdminInlineAdmin
    ]


admin.site.register(ConsultationEntrySheetSaleHeader, ConsultationEntrySheetSaleHeaderAdmin)


# ############################### CONSULTATION SHEET SALE DETAIL
class ConsultationSheetSaleDetailResource(resources.ModelResource):

    class Meta:
        model = ConsultationSheetSaleDetail


class ConsultationSheetSaleDetailAdmin(ImportExportModelAdmin):
    resource_class = ConsultationSheetSaleDetailResource
    search_fields = ['id',
                     'description',
                     'consultation_sheet__patient__name',
                     'consultation_sheet__patient__last_name',
                     'created_at', 'updated_at'
                     ]

    list_display = (
        'id',
        'sale_header',
        'quantity',
        'description',
        'unit_price',
        'total_price',
        'currency',
        'consultation_sheet',
        'created_at',
        'updated_at'
    )


# admin.site.register(ConsultationSheetSaleDetail, ConsultationSheetSaleDetailAdmin)


# ############################### CONSULTATION SHEET SALE PAYMENT
class ConsultationSheetSalePaymentResource(resources.ModelResource):

    class Meta:
        model = ConsultationSheetSalePayment


class ConsultationSheetSalePaymentAdmin(ImportExportModelAdmin):
    resource_class = ConsultationSheetSalePaymentResource
    search_fields = ['id',
                     'observations',
                     'consultation_sheet__patient__name',
                     'consultation_sheet__patient__last_name',
                     'created_at', 'updated_at'
                     ]
    list_filter = [
        'payment_method',
        'currency'
    ]

    list_display = (
        'id',
        'sale',
        'amount',
        'currency',
        'payment_method',
        'payment_datetime',
        'observations',
        'consultation_sheet',
        'created_at',
        'updated_at'
    )


admin.site.register(ConsultationSheetSalePayment, ConsultationSheetSalePaymentAdmin)
