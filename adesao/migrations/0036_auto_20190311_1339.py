# Generated by Django 2.0.8 on 2019-03-11 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0035_sistemacultura_conselho_aux'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sistemacultura',
            name='conselho',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conselho', to='planotrabalho.ConselhoDeCultura'),
        ),
    ]