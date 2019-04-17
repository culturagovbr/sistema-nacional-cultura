# Generated by Django 2.0.8 on 2019-02-21 18:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0016_auto_20190221_1452'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE \
            planotrabalho_componente \
            RENAME CONSTRAINT \
            planotrabalho_compon_diligencia_id_308baa63_fk_gestao_di \
            TO planotrabalho_compon_diligencia_id_e34b9808_fk_gestao_di"
        ),
        migrations.RemoveField(
            model_name='componente',
            name='diligencia',
        ),
        migrations.RenameField(
            model_name='arquivocomponente2',
            old_name='diligencia_arquivo',
            new_name='diligencia',
        ),
    ]