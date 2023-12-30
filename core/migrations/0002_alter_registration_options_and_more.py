# Generated by Django 4.2.2 on 2023-12-29 23:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registration',
            options={'verbose_name': 'Inscripción', 'verbose_name_plural': 'Inscripciones'},
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='enable',
            new_name='enabled',
        ),
        migrations.AlterField(
            model_name='registration',
            name='student',
            field=models.ForeignKey(limit_choices_to={'groups__name': 'estudiantes'}, on_delete=django.db.models.deletion.CASCADE, related_name='students_registration', to=settings.AUTH_USER_MODEL, verbose_name='Estudiante'),
        ),
    ]