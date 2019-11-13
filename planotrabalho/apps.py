from django.apps import AppConfig


class PlanoTrabalhoConfig(AppConfig):
    name = 'planotrabalho'
    label = "planotrabalho"
    verbose_name = "Plano Trabalho"

    def ready(self):
        import planotrabalho.signals
