from django.dispatch import receiver
from simple_history.signals import pre_create_historical_record

from gestao.models import DiligenciaSimples, HistoricalDiligenciaSimples


@receiver(pre_create_historical_record, sender=HistoricalDiligenciaSimples)
def inclui_arquivo_no_historico_diligencia(sender, instance, history_instance, **kwargs):
    if instance.componente:
        url = instance.componente.all()[0].arquivo.url
        history_instance.arquivo_url = url
