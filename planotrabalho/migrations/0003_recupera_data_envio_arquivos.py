from os import stat

from datetime import datetime

from django.db import migrations, models


def recupera_data(apps, schema_editor):

    PlanoTrabalho = apps.get_model("planotrabalho", "PlanoTrabalho")
    componentes = (
        "criacao_sistema",
        "orgao_gestor",
        "conselho_cultural",
        "fundo_cultura",
        "plano_cultura",
    )
    planos = PlanoTrabalho.objects.filter(
        plano_cultura__isnull=False
    ).prefetch_related()

    for plano in planos:
        for componente in componentes:
            try:
                componente_plano = getattr(plano, componente)
                arquivo = componente_plano.arquivo.file
                stats = stat(str(arquivo))
                data = datetime.fromtimestamp(stats.st_mtime)
                componente_plano.data_envio = data
                componente_plano.save()
            except:
                pass


class Migration(migrations.Migration):

    dependencies = [("planotrabalho", "0002_migra_arquivos_componentes")]

    operations = [
        migrations.RunPython(recupera_data),
    ]
