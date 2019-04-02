from django.apps import AppConfig


class GestaoConfig(AppConfig):
    name = 'gestao'
    label = "gestao"
    verbose_name = "Gestao"

    def ready(self):
        import gestao.signals
        from simple_history.signals import pre_create_historical_record
        from .models import HistoricalDiligenciaSimples
