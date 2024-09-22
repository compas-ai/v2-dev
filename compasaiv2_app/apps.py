from django.apps import AppConfig


class Compasaiv2AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'compasaiv2_app'

    def ready(self):
        import compasaiv2_app.signals  # Import the signals