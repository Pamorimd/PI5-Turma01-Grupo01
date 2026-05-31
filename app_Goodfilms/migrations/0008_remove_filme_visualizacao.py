# Generated to remove movie view tracking

from django.db import migrations


def drop_visualizacao_table(apps, schema_editor):
    existing_tables = {
        table_name.lower()
        for table_name in schema_editor.connection.introspection.table_names()
    }

    if 'filme_visualizacao' in existing_tables:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('DROP TABLE Filme_visualizacao')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('app_Goodfilms', '0007_remove_unused_filme_columns'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(drop_visualizacao_table, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.DeleteModel(
                    name='Filme_visualizacao',
                ),
            ],
        ),
    ]
