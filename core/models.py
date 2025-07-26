from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# Create your models here.


# CURSOS
class Course(models.Model):
    STATUS_CHOICES = (
        ('I', 'En etapa de inscripción'),
        ('P', 'En progreso'),
        ('F', 'Finalizado'),
    )
    name = models.CharField(max_length=90, verbose_name='Nombre')
    description = models.TextField(
        verbose_name='Descripción', blank=True, null=True)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'profesores'}, verbose_name='profesor')
    class_quantity = models.PositiveIntegerField(
        default=0, verbose_name='Cantidad de clases')
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='I', verbose_name='Estado')
    capacity = models.PositiveIntegerField(
        default=0, verbose_name='Capacidad', help_text='Cantidad de alumnos que pueden inscribirse en el curso')
    start_date = models.DateField(
        verbose_name='Fecha de inicio', blank=True, null=True)
    end_date = models.DateField(
        verbose_name='Fecha de finalización', blank=True, null=True)

    def __str__(self):
        return self.name

    class meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['-id']


# INCRIPSCIONES
class Registration(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, verbose_name='Curso')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students_registration', limit_choices_to={
        'groups__name': 'estudiantes'}, verbose_name='Estudiante')
    enabled = models.BooleanField(default=True, verbose_name='Alumno Regular')

    def __str__(self):
        return f'{self.student.username} - {self.course.name}'

    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'


# ASISTENCIAS
class Attendance(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, verbose_name='Curso')
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='Attendance', limit_choices_to={'groups__name': 'estudiantes'}, verbose_name='estudiante')
    date = models.DateField(null=True, blank=True, verbose_name='Fecha')
    present = models.BooleanField(
        default=False, blank=True, null=True, verbose_name='Presente')

    # lOGICA PARA GENERAR EL ESTADO REGULAR /IRREGULAR(enable)
    # total de asistencias=> class_quantity del modulo Course
    # total inasistencias =>attendance => present =False
    # Porcentaje-inasistencia = (total_inasistencias/tataol_clases)*100 ------> >20 (>20)=> alumno es irregular =>enable=False
    def update_registration_enabled_status(self):
        course_instances = Course.objects.get(id=self.course.id)
        total_classes = course_instances.class_quantity
        total_absences = Attendance.objects.filter(
            student=self.student, course=self.course, present=False).count()
        absences_percent = (total_absences / total_classes) * 100
        registration = Registration.objects.get(
            student=self.student, course=self.course)
        if absences_percent > 20:
            registration.enable = False
        else:
            registration.enable = True
        registration.save()

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'

    def __str__(self):
        return f'Asistencia {self.id}'


# NOTAS
class Mark(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, verbose_name='Curso')
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'estudiantes'}, verbose_name='estudiantes')
    mark_1 = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Nota 1')
    mark_2 = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Nota 2')
    mark_3 = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='Nota 3')
    average = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Promedio')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de creación', blank=True, null=True)

    @property
    def marks(self):
        mark = []
        if self.mark_1 is not None:
            mark.append(f'Primera Evaluación: {self.mark_1}')
        if self.mark_2 is not None:
            mark.pop() if mark else None
            mark.append(f'Segunda Evaluación: { self.mark_2}')
        if self.mark_3 is not None:
            average = int(self.average)
            mark.pop() if mark else None
            mark.append(
                f'Tercera Evaluación: {self.mark_3}, Con promedio: {average:.1f}')
        return mark

    def __str__(self):
        return str(self.course)

    # Calcular el promedio (llamo a una función)
    def calculate_average(self):
        marks = [self.mark_1, self.mark_2, self.mark_3]
        valid_marks = [mark for mark in marks if mark is not None]
        if valid_marks:
            return sum(valid_marks) / len(valid_marks)
        return None

    def save(self, *args, **kwargs):
        # Verifico si alguna nota cambio
        if self.mark_1 or self.mark_2 or self.mark_3:
            # Calcular el promedio (llamo a una función)
            self.average = self.calculate_average()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'


class Notifications(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Usuario')
    message = models.TextField(verbose_name='Mensaje')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de creación')
    STATUS_CHOICES = (
        ('I', 'Inscripción'),
        ('P', 'Progreso'),
        ('F', 'Finalizado'),
        ('N', 'Nota'),
        ('A', 'Asignacion'),
    )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, verbose_name='Estado', default='N')

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'


# Guardar notas en la base de datos


@receiver(post_save, sender=Attendance)
@receiver(post_delete, sender=Attendance)
def update_registration_enabled_status(sender, instance, **kwargs):
    instance.update_registration_enabled_status()
