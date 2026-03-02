from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rea_common.views import BaseModelViewSet
from .serializers.shop import ShopSerializer
from .permissions import IsShopOwner, CanCreateShop, CanToggleActive, CanImport
from .models import Shop
from .services.import_products_service import ImportProductsService

class ShopViewSet(BaseModelViewSet):
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated, IsShopOwner, CanCreateShop, CanToggleActive, CanImport]

    def get_queryset(self):
        return Shop.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        shop = self.get_object()
        shop.active = not shop.active
        shop.save()

        return Response(self.get_serializer(shop).data)
    
    @action(detail=True, methods=['post'])
    def import_products(self, request, pk=None):
        shop = self.get_object()
        url = request.data.get('url')
        
        if not url:
            return Response(
                {'status': False, 'error': 'Не указан URL файла'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Используем сервис импорта
        service = ImportProductsService(request.user)
        result = service.import_from_url(url)
        
        if result.success:
            return Response(
                {
                    'status': True,
                    'message': result.message,
                    'statistics': {
                        'products_created': result.products_created,
                        'products_updated': result.products_updated,
                        'categories_created': result.categories_created,
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    'status': False,
                    'error': result.message
                },
                status=status.HTTP_400_BAD_REQUEST
            )