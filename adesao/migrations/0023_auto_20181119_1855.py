# Generated by Django 2.0.8 on 2018-11-19 20:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adesao', '0022_auto_20181023_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sistemacultura',
            name='cadastrador',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sistema_cultura', to='adesao.Usuario'),
        ),
    ]
