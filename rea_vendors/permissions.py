from rest_framework import permissions
from rea_users.models import CustomUser


class IsShopOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CanCreateShop(permissions.BasePermission):
    message = "Только продавцы могут создавать магазины"

    def has_permission(self, request, view):
        if view.action == 'create':
            if request.user.role != CustomUser.ROLE_VENDOR:
                return False
            
            if hasattr(request.user, 'shop'):
                self.message = "У вас уже есть магазин"
                return False
            
            return True
        
        return True
    

class CanToggleActive(permissions.BasePermission):
    message = "Только владелец может изменять статус магазина"

    def has_object_permission(self, request, view, obj):
        if view.action == 'toggle_active':
            return obj.user == request.user
        return True
    

class CanImport(permissions.BasePermission):
    message = "Только владелец может импортировать товары"

    def has_object_permission(self, request, view, obj):
        if view.action == 'import_products':
            return obj.user == request.user
        return True