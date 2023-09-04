# Generated by Django 4.2.2 on 2023-09-04 20:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='student',
            field=models.ForeignKey(limit_choices_to={'groups__name': 'Estudiantes'}, on_delete=django.db.models.deletion.CASCADE, related_name='Attendance', to=settings.AUTH_USER_MODEL, verbose_name='estudiante'),
        ),
        migrations.AlterField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(limit_choices_to={'groups__name': 'Profesores'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='profesor'),
        ),
        migrations.AlterField(
            model_name='mark',
            name='student',
            field=models.ForeignKey(limit_choices_to={'groups__name': 'Estudiantes'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='estudiantes'),
        ),
        migrations.AlterField(
            model_name='registration',
            name='student',
            field=models.ForeignKey(limit_choices_to={'groups__name': 'Estudiantes'}, on_delete=django.db.models.deletion.CASCADE, related_name='student_registration', to=settings.AUTH_USER_MODEL, verbose_name='estudiante'),
        ),
    ]
