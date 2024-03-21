from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from stock.models import Deposit, Product, StockMovement, Cart, CartDetail, ProductDepositQuantity


# Register your models here.
# Product Deposit Quantity Inline
class ProductDepositQuantityInlineAdmin(admin.TabularInline):
    model = ProductDepositQuantity
    readonly_fields = ['product', 'deposit', 'quantity']
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj):
        return False


# ####################################### DEPOSIT
class DepositResource(resources.ModelResource):

    class Meta:
        model = Deposit


class DepositAdmin(ImportExportModelAdmin):
    resource_class = DepositResource
    search_fields = ['id', 'name']
    list_filter = ['default_deposit', 'created_at', 'updated_at']

    list_display = (
        'id',
        'name',
        'default_deposit',
        'created_at',
        'updated_at'
    )
    inlines = [
        ProductDepositQuantityInlineAdmin
    ]

    change_form_template = 'admin/admin_update_deposit.html'


admin.site.register(Deposit, DepositAdmin)


# ###################################### PRODUCT
class ProductResource(resources.ModelResource):

    class Meta:
        model = Product


class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    search_fields = ['id', 'name', 'description']
    list_filter = ['currency', 'created_at', 'updated_at']

    list_display = (
        'id',
        'name',
        'description',
        'purchase_price',
        'sale_price',
        'currency',
        'created_at',
        'updated_at'

    )
    change_form_template = 'admin/admin_update_product.html'

    inlines = [
        ProductDepositQuantityInlineAdmin
    ]


admin.site.register(Product, ProductAdmin)


# ################################# STOCK MOVEMENT
class StockMovementResource(resources.ModelResource):

    class Meta:
        model = StockMovement


class StockMovementAdmin(ImportExportModelAdmin):
    resource_class = StockMovementResource
    search_fields = ['id', 'name', 'description', 'user__username', 'product__name', 'deposit__name']
    list_filter = ['type', 'created_at', 'updated_at']

    list_display = (
        'id',
        'type',
        'deposit',
        'product',
        'quantity',
        'description',
        'user',
        'created_at',
        'updated_at'
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(StockMovement, StockMovementAdmin)


# ######################################## CART DETAIL
class CartDetailResource(resources.ModelResource):

    class Meta:
        model = CartDetail


class CartDetailAdmin(ImportExportModelAdmin):
    resource_class = CartDetailResource
    search_fields = ['id', 'product__name']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'id',
        'cart',
        'product',
        'quantity',
        'created_at',
        'updated_at'
    )


# admin.site.register(CartDetail, CartDetailAdmin)


# Cart Detail Inline
class CartDetailInlineAdmin(admin.TabularInline):
    model = CartDetail


# ############################################ CART
class CartResource(resources.ModelResource):

    class Meta:
        model = Cart


class CartAdmin(ImportExportModelAdmin):
    esource_class = CartResource
    search_fields = ['id', 'deposit_in__name', 'deposit_out__name']
    list_filter = ['deposit_out', 'deposit_in', 'created_at', 'updated_at']

    list_display = (
        'id',
        'deposit_out',
        'deposit_in',
        'created_at',
        'updated_at'
    )

    inlines = [
        CartDetailInlineAdmin
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_formset(self, request, form, formset, change):
        cart_details = formset.save(commit=False)
        for cart_detail in cart_details:
            # Search for product stock
            product_deposit_out = ProductDepositQuantity.objects.filter(
                product=cart_detail.product,
                deposit=form.cleaned_data['deposit_out']
            ).first()

            product_deposit_in = ProductDepositQuantity.objects.filter(
                product=cart_detail.product,
                deposit=form.cleaned_data['deposit_in']
            ).first()

            if product_deposit_out is None:
                raise ValueError('There is no stock created for ' + str(cart_detail.product) + ' in ' + str(form.cleaned_data['deposit_out']))

            if product_deposit_in is None:
                raise ValueError('There is no stock created for ' + str(cart_detail.product) + ' in ' + str(form.cleaned_data['deposit_in']))

            # Create a susbtraction Stock Movement from deposit out.
            new_substraction_movement = StockMovement.objects.create(
                type=StockMovement.OUT_MOVEMENT_TYPE,
                deposit=form.cleaned_data['deposit_out'],
                product=cart_detail.product,
                quantity=cart_detail.quantity,
                user=request.user,
                description='Substraction Movement from cart interface.'
            )
            print('Substraction Movement created ' + str(new_substraction_movement.id))

            # Create an addition Stock Movement for deposit in.
            new_addition_movement = StockMovement.objects.create(
                type=StockMovement.IN_MOVEMENT_TYPE,
                deposit=form.cleaned_data['deposit_in'],
                product=cart_detail.product,
                quantity=cart_detail.quantity,
                user=request.user,
                description='Adittion Movement from cart interface.'
            )
            print('Addition Movement created ' + str(new_addition_movement))

            cart_detail.save()

        formset.save_m2m()


admin.site.register(Cart, CartAdmin)


# ######################################### Product Deposit Quantity
class ProductDepositQuantityResource(resources.ModelResource):

    class Meta:
        model = ProductDepositQuantity


class ProductDepositQuantityAdmin(ImportExportModelAdmin):
    resource_class = ProductDepositQuantityResource
    search_fields = ['id', 'deposit__name', 'product__name']
    list_filter = ['deposit', 'created_at', 'updated_at']

    list_display = (
        'id',
        'deposit',
        'product',
        'quantity',
        'created_at',
        'updated_at'
    )


# admin.site.register(ProductDepositQuantity, ProductDepositQuantityAdmin)

