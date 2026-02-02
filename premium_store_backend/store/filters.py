from django_filters.rest_framework import FilterSet

from .models import Service, Order

class ServiceFilter(FilterSet):
    class Meta:
        model = Service
        fields = {
            'price': ['range'],
            'discounts': ['exact'],
        }


class OrderFilter(FilterSet):
    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
        }