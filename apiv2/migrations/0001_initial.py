from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension

# Adiciona a extensão UnaccentExtension para tratar pesquisas na API
# em strings que tenham acento 

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        UnaccentExtension()
    ]