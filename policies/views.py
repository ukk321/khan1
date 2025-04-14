import logging
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.generics import ListAPIView, get_object_or_404

from policies.models import PolicyModel, DealModel
from policies.serializers import PolicySerializer
from services.models import ServiceModel, CategoryModel, SubServicesModel


logger = logging.getLogger(__name__)


# Create your views here.
class PolicyView(ListAPIView):
    serializer_class = PolicySerializer

    def get_queryset(self):
        return PolicyModel.objects.filter(is_active=True)


def create_deal(request):
    if request.method == 'POST':
        deal_name = request.POST.get('deal_name')
        total_price = request.POST.get('deal_price')
        discounted_price = request.POST.get('deal_discounted_price')
        is_active = request.POST.get('deal_is_active') == 'on'
        selected_services = request.POST.getlist('services')
        selected_categories = request.POST.getlist('categories')
        selected_subservices = request.POST.getlist('subservices')
        selected_nested_subservices = request.POST.getlist('nested_subservices')
        selected_sub_nested_subservices = request.POST.getlist('sub_nested_subservices')

        if deal_name and total_price is not None and discounted_price is not None:
            try:
                if DealModel.objects.filter(name=deal_name).exists():
                    messages.error(request, 'Deal with this name already exists')
                    return redirect('admin:policies_dealmodel_changelist')

                total_price = float(total_price)
                discounted_price = float(discounted_price)
                deal = DealModel.objects.create(
                    name=deal_name,
                    price=total_price,
                    discounted_price=discounted_price,
                    is_active=is_active,
                    created_by=request.user,
                    updated_by=request.user
                )

                if selected_services:
                    services = ServiceModel.objects.filter(id__in=selected_services)
                    deal.service_title.set(services)

                if selected_categories:
                    categories = CategoryModel.objects.filter(id__in=selected_categories)
                    deal.category.set(categories)

                all_subservices = selected_subservices + selected_nested_subservices + selected_sub_nested_subservices
                if all_subservices:
                    subservices = SubServicesModel.objects.filter(id__in=all_subservices)
                    deal.subservice.set(subservices)

                deal.save()

                messages.success(request, 'Deal created successfully!')
                return redirect('admin:policies_dealmodel_changelist')
            except ValueError:
                messages.error(request, 'Invalid price value')
                return redirect('admin:policies_dealmodel_changelist')
        else:
            messages.error(request, 'Invalid data')
            return redirect('admin:policies_dealmodel_changelist')

    return JsonResponse({'success': False, 'error': 'Invalid request method'},status=400)


def fetch_deals(request):
    deals = DealModel.objects.filter(is_active=True)
    deal_list = []
    for deal in deals:
        included_items = []

        subservices = deal.subservice.all()
        for subservice in subservices:
            category = subservice.category
            service = category.service
            included_items.append(f"{subservice.name} ({service.name}, {category.name})")

        for subservice in subservices:
            included_items.append(subservice.name)

        deal_data = {
            'id': deal.id,
            'name': deal.name,
            'price': deal.price,
            'discounted_price': deal.discounted_price,
            'included_items': included_items,
            'is_active': deal.is_active
        }

        deal_list.append(deal_data)

    return JsonResponse(deal_list, safe=False)


def fetch_all_deals_for_template(request):
    deals = DealModel.objects.all()  # Fetch all deals, regardless of is_active status
    deal_list = []
    for deal in deals:
        included_items = []

        subservices = deal.subservice.all()
        for subservice in subservices:
            category = subservice.category
            service = category.service
            included_items.append(f"{subservice.name} ({service.name}, {category.name})")

        for subservice in subservices:
            included_items.append(subservice.name)

        deal_data = {
            'id': deal.id,
            'name': deal.name,
            'price': deal.price,
            'discounted_price': deal.discounted_price,
            'included_items': included_items,
            'is_active': deal.is_active
        }

        deal_list.append(deal_data)

    return JsonResponse(deal_list, safe=False)


def check_deal_name(request):
    deal_name = request.GET.get('deal_name')
    if DealModel.objects.filter(name=deal_name).exists():
        return JsonResponse({'exists': True})
    return JsonResponse({'exists': False})


def delete_deal(request, deal_id):
    if request.method == 'POST':
        deal = get_object_or_404(DealModel, id=deal_id)
        deal.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

