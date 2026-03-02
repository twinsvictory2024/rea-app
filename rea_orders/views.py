from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem, Product
from rea_users.models import Contact, CustomUser
from .serializers.order import OrderSerializer
from .serializers.order_item import OrderItemVendorSerializer
from .permissions import IsOrderOwner
from rea_common.views import BaseListAPIView
from .tasks import send_customer_new_order_email, send_vendor_new_order_email


class OrderShowView(APIView):
    permission_classes = [IsAuthenticated, IsOrderOwner]
    
    def get(self, request, order_id=None):
        """
        Просмотр заказа (корзины).
        Если order_id не передан - возвращаем текущую корзину пользователя
        """
        if order_id:
            order = get_object_or_404(Order, id=order_id, user=request.user)
        else:
            # Ищем активную корзину пользователя
            order = Order.objects.filter(
                user=request.user,
                state=Order.STATE_BASKET
            ).first()
            
            if not order:
                # Если корзины нет, возвращаем пустой ответ
                return Response({'detail': 'Корзина пуста'}, status=status.HTTP_200_OK)
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderAddItemView(APIView):
    permission_classes = [IsAuthenticated, IsOrderOwner]
    
    def post(self, request):
        """
        Добавление товара в корзину.
        Ожидает: { "order_id": "optional-uuid", "product_id": "uuid", "qty": 1 }
        """
        product_id = request.data.get('product_id')
        qty = int(request.data.get('qty', 1))
        order_id = request.data.get('order_id')
        
        if not product_id:
            return Response(
                {'error': 'Не указан товар'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if qty <= 0:
            return Response(
                {'error': 'Количество должно быть положительным'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем существование товара и его наличие
        product = get_object_or_404(Product, id=product_id)
        
        # Проверяем остаток
        if product.stock < qty:
            return Response(
                {
                    'error': 'Недостаточно товара на складе',
                    'available': product.stock,
                    'requested': qty
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Получаем или создаем корзину
            if order_id:
                order = get_object_or_404(
                    Order, 
                    id=order_id, 
                    user=request.user,
                    state=Order.STATE_BASKET
                )
            else:
                order = Order.objects.filter(
                    user=request.user,
                    state=Order.STATE_BASKET
                ).first()
                
                if not order:
                    order = Order.objects.create(
                        user=request.user,
                        state=Order.STATE_BASKET
                    )
            
            # Добавляем или обновляем позицию
            try:
                order_item, created = OrderItem.objects.get_or_create(
                    order=order,
                    product=product,
                    defaults={'qty': qty}
                )
                
                if not created:
                    # Проверяем общее количество с учетом существующего
                    total_qty = order_item.qty + qty
                    if product.stock < total_qty:
                        return Response(
                            {
                                'error': 'Общее количество превышает остаток',
                                'available': product.stock,
                                'in_cart': order_item.qty,
                                'requested_add': qty
                            }, 
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    order_item.qty = total_qty
                    order_item.save()
                    
            except IntegrityError:
                return Response(
                    {'error': 'Ошибка при добавлении товара'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderRemoveItemView(APIView):
    permission_classes = [IsAuthenticated, IsOrderOwner]
    
    def delete(self, request, order_id, item_id):
        """
        Удаление позиции из заказа
        """
        order = get_object_or_404(
            Order, 
            id=order_id, 
            user=request.user,
            state=Order.STATE_BASKET
        )
        
        order_item = get_object_or_404(OrderItem, id=item_id, order=order)
        order_item.delete()
        
        # Если после удаления корзина пуста - можно оставить или удалить
        if not order.order_items.exists():
            order.delete()
            return Response(
                {'detail': 'Корзина очищена'}, 
                status=status.HTTP_200_OK
            )
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderIncrementItemView(APIView):
    permission_classes = [IsAuthenticated, IsOrderOwner]
    
    def post(self, request, order_id, item_id):
        """
        Увеличение количества товара
        """
        order = get_object_or_404(
            Order, 
            id=order_id, 
            user=request.user,
            state=Order.STATE_BASKET
        )
        
        order_item = get_object_or_404(OrderItem, id=item_id, order=order)
        
        # Проверяем наличие на складе
        if order_item.product.stock < order_item.qty + 1:
            return Response(
                {
                    'error': 'Недостаточно товара на складе',
                    'available': order_item.product.stock,
                    'in_cart': order_item.qty
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order_item.qty += 1
        order_item.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    

class OrderDecrementItemView(APIView):
    permission_classes = [IsAuthenticated, IsOrderOwner]
    
    def post(self, request, order_id, item_id):
        """
        Уменьшение количества товара
        """
        order = get_object_or_404(
            Order, 
            id=order_id, 
            user=request.user,
            state=Order.STATE_BASKET
        )
        
        order_item = get_object_or_404(OrderItem, id=item_id, order=order)
        
        if order_item.qty > 1:
            order_item.qty -= 1
            order_item.save()
        else:
            # Если количество становится 0 - удаляем позицию
            order_item.delete()
            
            if not order.order_items.exists():
                order.delete()
                return Response(
                    {'detail': 'Корзина очищена'}, 
                    status=status.HTTP_200_OK
                )
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderConfirmView(APIView):
    permission_classes = [IsAuthenticated, IsOrderOwner]
    
    def post(self, request, order_id):
        """
        Подтверждение заказа.
        Ожидает: { "contact_id": "uuid" }
        """
        contact_id = request.data.get('contact_id')
        
        if not contact_id:
            return Response(
                {'error': 'Не указан контакт'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = get_object_or_404(
            Order, 
            id=order_id, 
            user=request.user,
            state=Order.STATE_BASKET
        )
        
        # Проверяем, что корзина не пуста
        if not order.order_items.exists():
            return Response(
                {'error': 'Нельзя подтвердить пустую корзину'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем наличие товаров
        stock_ok, insufficient_items = order.check_stock()
        if not stock_ok:
            return Response(
                {
                    'error': 'Недостаточно товаров на складе',
                    'insufficient_items': insufficient_items
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, что контакт принадлежит пользователю
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
        
        with transaction.atomic():
            # Резервируем товары
            order.reserve_stock()
            
            # Обновляем заказ
            order.contact = contact
            order.state = Order.STATE_NEW
            order.save()
            
        self.send_notification_emails(order)
        
        serializer = OrderSerializer(order)
        return Response({
            'order': serializer.data,
            'message': 'Заказ успешно оформлен',
            'total_price': order.total_price_display
        })
    
    def send_notification_emails(self, order):
        # 1. Отправляем email заказчику
        send_customer_new_order_email.delay(
            order_id=str(order.id),
            customer_email=order.user.email
        )
        
        # 2. Отправляем email каждому вендору
        vendor_emails = CustomUser.objects.filter(
            role=CustomUser.ROLE_VENDOR,
            shop__product_infos__order_items__order=order
        ).distinct().values_list('email', flat=True)
        
        for vendor_email in vendor_emails:
            send_vendor_new_order_email.delay(
                vendor_email=vendor_email,
                order_id=str(order.id)
            )


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated, IsOrderOwner]
    
    def post(self, request, order_id):
        """
        Отмена заказа с возвратом товаров на склад
        """
        order = get_object_or_404(
            Order, 
            id=order_id, 
            user=request.user
        )
        
        # Проверяем, можно ли отменить заказ
        cancellable_states = [Order.STATE_NEW, Order.STATE_CONFIRMED]
        if order.state not in cancellable_states:
            return Response(
                {'error': f'Заказ в статусе {order.state} нельзя отменить'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Возвращаем товары на склад
            order.release_stock()
            
            # Меняем статус
            order.state = Order.STATE_CANCELED
            order.save()
        
        serializer = OrderSerializer(order)
        return Response({
            'order': serializer.data,
            'message': 'Заказ отменен, товары возвращены на склад'
        })
    

class OrderListView(BaseListAPIView):
    def get_serializer_class(self):
        user = self.request.user
        
        if user.role == CustomUser.ROLE_CUSTOMER:
            return OrderSerializer
        elif user.role == CustomUser.ROLE_VENDOR:
            return OrderItemVendorSerializer
        return None
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == CustomUser.ROLE_CUSTOMER:
            return Order.objects.filter(
                user=user
            ).exclude(
                state=Order.STATE_BASKET
            ).prefetch_related(
                'order_items__product',
                'contact'
            )
            
        elif user.role == CustomUser.ROLE_VENDOR:
            return OrderItem.objects.filter(
                product__shop__user=user
            ).exclude(
                order__state=Order.STATE_BASKET
            ).select_related(
                'product',
                'order',
                'order__user',
                'order__contact'
            )
            
        return Order.objects.none()