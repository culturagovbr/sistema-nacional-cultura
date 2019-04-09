from django.db.models.signals import post_save
from django.dispatch import receiver

from gestao.models import DiligenciaSimples
from planotrabalho.models import ArquivoComponente2
from planotrabalho.models import Componente
from planotrabalho.models import ConselhoDeCultura
from planotrabalho.models import FundoDeCultura


@receiver(post_save, sender=ArquivoComponente2)
@receiver(post_save, sender=Componente)
@receiver(post_save, sender=ConselhoDeCultura)
@receiver(post_save, sender=FundoDeCultura)
def inclui_arquivo_no_historico_diligencia(sender, instance, **kwargs):
    if kwargs['update_fields'] and "diligencia" in kwargs['update_fields']:
        url = instance.arquivo.url
        ultimo_historico = instance.diligencia.history.latest()
        ultimo_historico.arquivo_url = url
        ultimo_historico.save()
