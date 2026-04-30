# Generated to remove unused movie columns from the database

from django.db import migrations


def remove_unused_filme_columns(apps, schema_editor):
    Filme = apps.get_model('app_Goodfilms', 'Filme')
    table_name = Filme._meta.db_table

    with schema_editor.connection.cursor() as cursor:
        existing_columns = {
            column.name.lower()
            for column in schema_editor.connection.introspection.get_table_description(
                cursor,
                table_name,
            )
        }

    for field_name in ('titulo_original', 'metadados', 'poster'):
        field = Filme._meta.get_field(field_name)
        if field.column.lower() in existing_columns:
            schema_editor.remove_field(Filme, field)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('app_Goodfilms', '0006_filme_user'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(remove_unused_filme_columns, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='filme',
                    name='titulo_original',
                ),
                migrations.RemoveField(
                    model_name='filme',
                    name='metadados',
                ),
                migrations.RemoveField(
                    model_name='filme',
                    name='poster',
                ),
            ],
        ),
    ]
