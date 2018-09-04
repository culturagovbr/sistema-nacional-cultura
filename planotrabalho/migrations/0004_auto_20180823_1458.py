# Generated by Django 2.0.8 on 2018-08-23 17:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planotrabalho', '0003_recupera_data_envio_arquivos'),
    ]

    operations = [
        migrations.AddField(
            model_name='conselhocultural',
            name='data_publicacao',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criacaosistema',
            name='data_publicacao',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='fundocultura',
            name='data_publicacao',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orgaogestor',
            name='data_publicacao',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='planocultura',
            name='data_publicacao',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='conselhocultural',
            name='situacao',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='conselhocultural_situacao', to='planotrabalho.SituacoesArquivoPlano'),
        ),
        migrations.AlterField(
            model_name='criacaosistema',
            name='situacao',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='criacaosistema_situacao', to='planotrabalho.SituacoesArquivoPlano'),
        ),
        migrations.AlterField(
            model_name='fundocultura',
            name='situacao',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='fundocultura_situacao', to='planotrabalho.SituacoesArquivoPlano'),
        ),
        migrations.AlterField(
            model_name='orgaogestor',
            name='situacao',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='orgaogestor_situacao', to='planotrabalho.SituacoesArquivoPlano'),
        ),
        migrations.AlterField(
            model_name='planocultura',
            name='situacao',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='planocultura_situacao', to='planotrabalho.SituacoesArquivoPlano'),
        ),
    ]