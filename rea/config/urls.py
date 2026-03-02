from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('api/auth/', include('rea_auth.urls')),
    path('api/auth/password_reset/', include('django_rest_passwordreset.urls')),
    path('api/users/', include('rea_users.urls')),
    path('api/vendors/', include('rea_vendors.urls')),
    path('api/catalog/', include('rea_catalog.urls')),
    path('api/orders/', include('rea_orders.urls')),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
        print("✓ Debug toolbar URLs added")
    except ImportError:
        print("✗ Debug toolbar not installed")
        pass