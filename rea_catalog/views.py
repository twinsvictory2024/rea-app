from django.shortcuts import render
from rea_common.views import BaseListAPIView
from rest_framework.mixins import RetrieveModelMixin
from .models import Category, Product
from rea_catalog.serializers.category import CategorySerializer
from rea_catalog.serializers.product import ProductSerializer, ProductListSerializer
from .filters import CategoryFilter, ProductFilter


class CategoryView(BaseListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter


class ProductView(BaseListAPIView):
    queryset = Product.objects.filter(shop__active=True)
    serializer_class = ProductListSerializer
    filterset_class = ProductFilter


class ProductDetailView(RetrieveModelMixin, BaseListAPIView):
    queryset = Product.objects.filter(shop__active=True)
    serializer_class = ProductSerializer
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)