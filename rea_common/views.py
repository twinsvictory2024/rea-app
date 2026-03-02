from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rea_common.services.pagination import Pagination
from rest_framework.generics import ListAPIView


class BaseModelViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = Pagination

class BaseListAPIView(ListAPIView):
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = Pagination