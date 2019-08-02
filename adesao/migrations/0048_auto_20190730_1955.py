# Generated by Django 2.0.8 on 2019-07-30 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0047_sistemacultura_oficio_prorrogacao_prazo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sistemacultura',
            name='oficio_cadastrador',
            field=models.FileField(max_length=255, null=True, upload_to='oficio_cadastrador'),
        ),
        migrations.AlterField(
            model_name='sistemacultura',
            name='oficio_prorrogacao_prazo',
            field=models.FileField(max_length=255, null=True, upload_to='oficio_prorrogacao_prazo'),
        ),
    ]
