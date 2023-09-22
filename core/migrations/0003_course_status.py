# Generated by Django 4.2.2 on 2023-09-22 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_attendance_student_alter_course_teacher_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='status',
            field=models.CharField(choices=[('I', 'En etapa de inscripción'), ('P', 'En progreso'), ('F', 'Finalizado')], default='I', max_length=1, verbose_name='Estado'),
        ),
    ]