from django.utils import timezone
from softdelete.models import SoftDeleteObject
from base.models import TimeStampModel, Currency
from django.db import models
from consultation.models import ConsultationSheet, ConsultationEntrySheet
from invoicing.models import PaymentMethod
from django.utils.translation import ugettext_lazy as _


# ################################### ABSTRAC SALE HEADER
class SaleHeader(models.Model):
    client_name = models.CharField(
        verbose_name=_('Client Name'),
        max_length=150, null=False, blank=False
    )
    client_tax_identification_number = models.CharField(
        verbose_name=_('Client Tax Identification Number'),
        max_length=50, null=True, blank=True
    )
    sale_date = models.DateTimeField(
        verbose_name=_('Sale Date'),
        null=False, blank=False,
        default=timezone.now
    )
    sale_total = models.FloatField(
        verbose_name=_('Sale Total'),
        null=False, blank=False,
        default=0
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='sales_headers'
    )

    class Meta:
        abstract = True


# ################################### ABSTRAC SALE DETAIL
class SaleDetail(models.Model):
    # sale_header = models.ForeignKey(
    #     to=SaleHeader, on_delete=models.CASCADE,
    #     verbose_name=_('Sale Header'),
    #     null=False, blank=False,
    #     related_name='sale_details'
    # ) THIS GOES IN THE CHILD CLASS WITH DIFERENT FIELD to=CUSTOMSaleHeader
    quantity = models.IntegerField(
        verbose_name=_('Quantity'),
        null=False, blank=False,
        default=1
    )
    description = models.CharField(
        verbose_name=_('Description'),
        max_length=250,
        null=False, blank=False,
        default=''
    )
    unit_price = models.FloatField(
        verbose_name=_('Unit price'),
        null=False, blank=False,
        default=0
    )
    total_price = models.FloatField(
        verbose_name=_('Total Price'),
        null=False, blank=False,
        default=0
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='sales_details'
    )

    class Meta:
        abstract = True


# ################################### ABSTRACT SALE PAYMENT
class SalePayment(models.Model):
    # sale = models.ForeignKey(
    #     verbose_name=_('Sale'),
    #     to=SaleHeader, on_delete=models.PROTECT,
    #     null=False, blank=False,
    #     related_name='sale_payments'
    # ) THIS GOES IN THE CHILD CLASS WITH DIFERENT FIELD to=CUSTOMSaleHeader
    amount = models.FloatField(
        verbose_name=_('Amount'),
        null=False, blank=True,
        default=0
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='sales_payments'
    )
    payment_method = models.ForeignKey(
        verbose_name=_('Payment Method'),
        to=PaymentMethod, on_delete=models.PROTECT,
        null=False, blank=False,
    )
    payment_datetime = models.DateTimeField(
        verbose_name=_('Payment Date'),
        null=False, blank=False,
        default=timezone.now
    )
    observations = models.TextField(
        verbose_name=_('Observations'),
        null=True, blank=True,
        default=''
    )

    class Meta:
        abstract = True


# ############################# CONSULTATION ENTRY SHEET SALE HEADER
class ConsultationEntrySheetSaleHeader(SaleHeader, TimeStampModel, SoftDeleteObject):
    consultation_entry_sheet = models.ForeignKey(
        verbose_name=_('Consultation Entry Sheet'),
        to=ConsultationEntrySheet, on_delete=models.PROTECT,
        null=False, blank=False,
        related_name='sale_header'
    )

    class Meta:
        verbose_name = _('Consultation Sheet Sale Header')
        verbose_name_plural = _('Consultation Sheets Sales Headers')

    def __str__(self):
        return self.client_name + str(self.consultation_entry_sheet) + self.sale_date.strftime("%d/%m/%Y %H:%M")


# ############################## CONSULTATION SHEET SALE DETAIL
class ConsultationSheetSaleDetail(SaleDetail, TimeStampModel, SoftDeleteObject):
    sale_header = models.ForeignKey(
        to=ConsultationEntrySheetSaleHeader, on_delete=models.CASCADE,
        verbose_name=_('Sale Header'),
        null=False, blank=False,
        related_name='sale_details'
    )
    consultation_sheet = models.ForeignKey(
        verbose_name=_('Consultation Sheet'),
        to=ConsultationSheet, on_delete=models.PROTECT,
        related_name='sale_details',
        null=True, blank=True,
        default=True,
    )

    class Meta:
        verbose_name = _('Consultation Sheet Sale Detail')
        verbose_name_plural = _('Consultation Sheets Sales Details')

    def __str__(self):
        return str(self.sale_header) + ' - (' + str(self.quantity) + ')' + self.description


# ################################### CONSULTATION SHEET SALE PAYMENT
class ConsultationSheetSalePayment(SalePayment, SoftDeleteObject, TimeStampModel):
    sale = models.ForeignKey(
        verbose_name=_('Sale'),
        to=ConsultationEntrySheetSaleHeader, on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='sale_payments'
    )
    consultation_sheet = models.ForeignKey(
        verbose_name=_('Consultation Sheet'),
        to=ConsultationSheet, on_delete=models.PROTECT,
        related_name='sale_payments',
        null=True, blank=True,
        default=True,
    )

    class Meta:
        verbose_name = _('Consultation Sheet Sale Payment')
        verbose_name_plural = _('Consultation Sheets Sales Payments')

    def __str__(self):
        return str(self.sale.client_name) + ' - ' + str(self.amount) + ' - ' + self.payment_datetime.strftime("%d/%m/%Y %H:%M")
