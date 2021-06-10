from django.apps import AppConfig


class LeadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leads'

    def ready(self):
        from leads import schedulercheck
        schedulercheck.start()