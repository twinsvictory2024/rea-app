from django.apps import AppConfig


class ReaAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rea_auth'

    def ready(self):
        import rea_auth.signals