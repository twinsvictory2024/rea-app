from .base import *
from .base import env

# Development specific settings
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# CORS for development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:9000',
    'http://127.0.0.1:9000',
    'http://localhost:8000',
]

CORS_ALLOW_ALL_ORIGINS = True  # Only for development!

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:9000',
    'http://127.0.0.1:9000',
    'http://localhost:8000',
]

# Disable HTTPS redirect
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email backend for development (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug Toolbar (optional)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

# More verbose logging for development
LOGGING['root']['level'] = 'DEBUG'