from django.contrib.auth.models import User
from django.db import models
from softdelete.models import SoftDeleteObject
from base.models import TimeStampModel, Currency
from django.utils.translation import ugettext_lazy as _
from auditlog.registry import auditlog


# Deposit
class Deposit(SoftDeleteObject, TimeStampModel):
    name = models.CharField(
        max_length=100, verbose_name=_('Name'),
        null=False, blank=False
    )
    default_deposit = models.BooleanField(
        verbose_name=_('Default Deposit'),
        default=False
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Deposit")
        verbose_name_plural = _("Deposits")

    def save(self, *args, **kwargs):
        if self.default_deposit:
            try:
                temp = Deposit.objects.get(default_deposit=True)
                if self != temp:
                    temp.default_deposit = False
                    temp.save()
            except Deposit.DoesNotExist:
                pass
        super(Deposit, self).save(*args, **kwargs)


auditlog.register(Deposit)


# Product
class Product(SoftDeleteObject, TimeStampModel):
    name = models.CharField(
        max_length=100, verbose_name=_('Name'),
        null=False, blank=False
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=False, blank=False
    )
    purchase_price = models.FloatField(
        verbose_name=_('Purchase price'),
        null=False, blank=False
    )
    sale_price = models.FloatField(
        verbose_name=_('Sale price'),
        null=False, blank=False
    )
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='products'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


auditlog.register(Product)


# Product Deposit Quantity
class ProductDepositQuantity(SoftDeleteObject, TimeStampModel):
    deposit = models.ForeignKey(
        to=Deposit, on_delete=models.PROTECT,
        verbose_name=_('Deposit'),
        null=False, blank=False,
        related_name='product_deposit_quantity'
    )
    product = models.ForeignKey(
        to=Product, on_delete=models.PROTECT,
        verbose_name=_('Product'),
        null=False, blank=False,
        related_name='product_deposit_quantity'
    )
    quantity = models.FloatField(
        verbose_name=_('Quantity'),
        null=False, blank=False,
    )

    def __str__(self):
        return str(self.deposit) + ' - ' + str(self.product) + ' -  ' + str(self.quantity)

    class Meta:
        unique_together = ('deposit', 'product')
        verbose_name = _("Product Deposit Quantity")
        verbose_name_plural = _("Products Deposits Quantitys")


auditlog.register(ProductDepositQuantity)


# Stock Movement
class StockMovement(SoftDeleteObject, TimeStampModel):
    IN_MOVEMENT_TYPE = 0
    OUT_MOVEMENT_TYPE = 1
    MOVEMENT_TYPES = (
        (IN_MOVEMENT_TYPE, _('IN')),
        (OUT_MOVEMENT_TYPE, _('OUT')),
    )
    deposit = models.ForeignKey(
        verbose_name=_('Deposit'),
        to=Deposit, on_delete=models.PROTECT,
        null=False, blank=False,
        related_name='stock_movements'
    )
    product = models.ForeignKey(
        verbose_name=_('Product'),
        to=Product, on_delete=models.PROTECT,
        null=False, blank=False,
        related_name='stock_movements'
    )
    type = models.IntegerField(
        verbose_name=_('Movement Type'),
        choices=MOVEMENT_TYPES,
        null=False, blank=False
    )
    quantity = models.FloatField(
        verbose_name=_('Quantity'),
        null=False, blank=False,
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=False, blank=False
    )

    user = models.ForeignKey(
        verbose_name=_('User'),
        to=User, on_delete=models.PROTECT,
        null=False, blank=False,
        related_name='stock_movements'
    )

    def __str__(self):
        return str(self.get_type_display()) + ' movement - deposit ' + str(self.deposit) + ' - product ' + str(self.product)

    class Meta:
        verbose_name = _("Stock Movement")
        verbose_name_plural = _("Stock Movements")

    def save(self, *args, **kwargs):
        super(StockMovement, self).save(*args, **kwargs)
        product_stock = ProductDepositQuantity.objects.filter(
            product=self.product,
            deposit=self.deposit
        ).first()

        # If stock exist
        if product_stock:
            # Adding to deposit
            if self.type == StockMovement.IN_MOVEMENT_TYPE:
                product_stock.quantity = product_stock.quantity + self.quantity
                product_stock.save()
            # Substracting from deposit
            else:
                new_quantity = product_stock.quantity - self.quantity
                product_stock.quantity = new_quantity
                product_stock.save()

                print('Product Stock Updated!')
        # If stock does not exist
        else:
            # Create a product deposit stock
            product_stock = ProductDepositQuantity.objects.create(
                deposit=self.deposit,
                product=self.product,
                quantity=self.quantity
            )
            print('Product Stock Created! ' + str(product_stock))


auditlog.register(StockMovement)


# Cart
class Cart(SoftDeleteObject, TimeStampModel):
    deposit_out = models.ForeignKey(
        to=Deposit, on_delete=models.PROTECT,
        verbose_name=_('Deposit Out'),
        null=False, blank=False,
        related_name='carts_deposit_out'
    )
    deposit_in = models.ForeignKey(
        to=Deposit, on_delete=models.PROTECT,
        verbose_name=_('Deposit In'),
        null=False, blank=False,
        related_name='carts_deposit_in'
    )

    def __str__(self):
        return _('Deposit out: ') + str(self.deposit_out) + ' to Deposit in: ' + str(self.deposit_in)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")


auditlog.register(Cart)


# Cart Detail
class CartDetail(SoftDeleteObject, TimeStampModel):
    cart = models.ForeignKey(
        to=Cart, on_delete=models.PROTECT,
        verbose_name=_('Cart'),
        related_name='cart_details',
        null=False, blank=False
    )
    product = models.ForeignKey(
        to=Product, on_delete=models.PROTECT,
        verbose_name=_('Product'),
        related_name='cart_details',
        null=False, blank=False
    )
    quantity = models.FloatField(
        verbose_name=_('Quantity'),
        null=False, blank=False
    )

    def __str__(self):
        return str(self.cart) + ' - ' + str(self.product) + ' - ' + str(self.quantity)

    class Meta:
        verbose_name = _("Cart Detail")
        verbose_name_plural = _("Cart Details")


auditlog.register(CartDetail)
