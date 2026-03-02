from django.urls import path
from .views import CategoryView, ProductView, ProductDetailView

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='categories'),
    path('products/', ProductView.as_view(), name='products'),
    path('products/<uuid:pk>/', ProductDetailView.as_view(), name='product')
]