# Generated to repair databases where the visualizacao table is missing

from django.db import migrations


def create_missing_visualizacao_table(apps, schema_editor):
    FilmeVisualizacao = apps.get_model('app_Goodfilms', 'Filme_visualizacao')
    existing_tables = {
        table_name.lower()
        for table_name in schema_editor.connection.introspection.table_names()
    }

    if FilmeVisualizacao._meta.db_table.lower() not in existing_tables:
        schema_editor.create_model(FilmeVisualizacao)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('app_Goodfilms', '0004_sync_filmes_columns'),
    ]

    operations = [
        migrations.RunPython(create_missing_visualizacao_table, migrations.RunPython.noop),
    ]
