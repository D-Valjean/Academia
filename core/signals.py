from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Registration, Mark


@receiver(post_save, sender=Registration)
def create_mark(sender, instance, created, **kwargs):
    if created:
        Mark.objects.create(student=instance.student,
                            course=instance.course,
                            mark_1=None,
                            mark_2=None,
                            mark_3=None,
                            average=None
                            )
