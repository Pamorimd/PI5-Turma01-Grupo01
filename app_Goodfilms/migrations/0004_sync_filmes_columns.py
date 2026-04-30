# Generated to repair databases where older Filme columns were missing

from django.db import migrations


def add_missing_filme_columns(apps, schema_editor):
    Filme = apps.get_model('app_Goodfilms', 'Filme')
    table_name = Filme._meta.db_table

    with schema_editor.connection.cursor() as cursor:
        existing_columns = {
            column.name
            for column in schema_editor.connection.introspection.get_table_description(
                cursor,
                table_name,
            )
        }

    for field_name in ('titulo_original', 'metadados', 'poster'):
        field = Filme._meta.get_field(field_name)
        if field.column not in existing_columns:
            schema_editor.add_field(Filme, field)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('app_Goodfilms', '0003_filme_classificacao_alter_filme_duracao_minutos'),
    ]

    operations = [
        migrations.RunPython(add_missing_filme_columns, migrations.RunPython.noop),
    ]
