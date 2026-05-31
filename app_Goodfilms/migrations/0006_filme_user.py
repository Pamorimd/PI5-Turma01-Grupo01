# Generated to make movies belong to the user who created them

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def add_filme_user_column(apps, schema_editor):
    Filme = apps.get_model('app_Goodfilms', 'Filme')
    User = apps.get_model('app_Goodfilms', 'CustomUser')
    table_name = Filme._meta.db_table
    column_names = {
        column.name.lower()
        for column in schema_editor.connection.introspection.get_table_description(
            schema_editor.connection.cursor(),
            table_name,
        )
    }

    if 'user_id' not in column_names:
        field = models.ForeignKey(
            User,
            on_delete=django.db.models.deletion.CASCADE,
            related_name='filmes',
            null=True,
            blank=True,
        )
        field.set_attributes_from_name('user')
        schema_editor.add_field(Filme, field)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('app_Goodfilms', '0005_sync_visualizacao_table'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_filme_user_column, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='filme',
                    name='user',
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='filmes',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
