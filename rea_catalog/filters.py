from django_filters.rest_framework import FilterSet, UUIDFilter, CharFilter, NumberFilter
from .models import Category, Product


class CategoryFilter(FilterSet):
    shops = UUIDFilter(
        field_name='shops__id',
        label='UUID магазина'
    )

    label = CharFilter(
        field_name='label',
        lookup_expr='icontains'
    )

    class Meta:
        model = Category
        fields = ['shops', 'label']


class ProductFilter(FilterSet):
    shop = UUIDFilter(
        field_name='shop',
        label='UUID магазина'
    )

    category = UUIDFilter(
        field_name='category',
        label='UUID категории'
    )

    label = CharFilter(
        field_name='label',
        lookup_expr='icontains'
    )

    price_min = NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Минимальная цена'
    )

    price_max = NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Максимальная цена'
    )

    class Meta:
        model = Product
        fields = ['shop', 'label', 'price_min', 'price_max']