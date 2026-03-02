from django.urls import path
from .views import (
    OrderShowView, 
    OrderAddItemView, 
    OrderRemoveItemView, 
    OrderIncrementItemView, 
    OrderDecrementItemView, 
    OrderConfirmView, 
    OrderCancelView,
    OrderListView
)

urlpatterns = [
    path('<uuid:order_id>/', OrderShowView.as_view(), name='order'),
    path('add/', OrderAddItemView.as_view(), name='add_item'),
    path('<uuid:order_id>/remove/<uuid:item_id>/', OrderRemoveItemView.as_view(), name='remove'),
    path('<uuid:order_id>/increment/<uuid:item_id>/', OrderIncrementItemView.as_view(), name='increment'),
    path('<uuid:order_id>/decrement/<uuid:item_id>/', OrderDecrementItemView.as_view(), name='decrement'),
    path('<uuid:order_id>/confirm/', OrderConfirmView.as_view(), name='confirm'),
    path('<uuid:order_id>/cancel/', OrderCancelView.as_view(), name='cancel'),
    path('', OrderListView.as_view(), name='list'),
]