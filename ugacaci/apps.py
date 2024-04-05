from django.apps import AppConfig


class UgacaciConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ugacaci'
    def ready(self):
        import ugacaci.signals
