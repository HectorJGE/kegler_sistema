from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView

from clinic.models import MedicalSupplyInsuranceAgreement, InsurancePlan, InsurancePlanMedicalSupplyFee
from stock.models import Product
from django.http import JsonResponse

# Create your views here.


# ############################################ PRODUCT

# Product Detail (JSON)
class ProductDetailJsonView(LoginRequiredMixin, DetailView):
    model = Product

    def get(self, request, *args, **kwargs):
        product_id = kwargs['pk']
        product = Product.objects.get(pk=product_id)
        price = product.sale_price

        insurance_plan_id = request.GET.get('insurance_plan_id')
        agreement_id = None

        if insurance_plan_id == '' or insurance_plan_id is None:
            cover_percentage = 0
            cover_amount = 0
            cover_type = 0
        else:
            insurance_plan = InsurancePlan.objects.get(pk=insurance_plan_id)
            # Get price from MedicalSupplyFee
            medical_supply_fee = InsurancePlanMedicalSupplyFee.objects.filter(
                insurance_plan=insurance_plan,
                medical_supply=product
            ).first()
            if medical_supply_fee:
                price = medical_supply_fee.price

            # Get Agreement cover percentage
            agreement = MedicalSupplyInsuranceAgreement.objects.filter(medical_supply=product, insurance_plan=insurance_plan).first()
            if agreement:
                cover_percentage = agreement.coverage_percentage
                agreement_id = agreement.id
                cover_amount = agreement.coverage_amount
                cover_type = agreement.cover_type
            else:
                cover_percentage = 0
                agreement_id = None
                cover_amount = 0
                cover_type = 0

        data = {
            'id': product.id,
            'name': product.name,
            'price': price,
            'currency': product.currency.id,
            'insurance_agreement_id': agreement_id,
            'insurance_coverage_percent': cover_percentage,
            'insurance_coverage_amount': cover_amount,
            'cover_type': cover_type

        }
        return JsonResponse(data, status=200, safe=False)
