from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Registration, Mark


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
