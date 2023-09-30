from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Registration, Mark, Attendance


@receiver(post_save, sender=Registration)
def create_marks(sender, instance, created, **kwargs):
    if created:
        Mark.objects.create(
            course=instance.course,
            student=instance.student,
            mark_1=None,
            mark_2=None,
            mark_3=None,
            average=None
        )


# Se;al para crear asistencias

@receiver(post_save, sender=Registration)
def create_attendance(sender, instance, created, **kwargs):
    if created:
        # crear un registro de asistencias por cada clase que tiene el curso(class_quantity)
        for i in range(1, instance.course.class_quantity + 1):
            Attendance.objects.create(
                course=instance.course,
                student=instance.student,
                date = None,
                present=True
            )
