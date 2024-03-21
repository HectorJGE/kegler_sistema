from django.urls import path

from stock.views import ProductDetailJsonView

urlpatterns = [
    # Product
    path('product/detail_json/<int:pk>/', ProductDetailJsonView.as_view(), name='product.detail_json'),

]