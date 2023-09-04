from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Profile


@receiver(post_save, sender=Profile)
def add_user_to_group(sender, instance, created, **kwargs):
    if created:
        try:
            perfil1 = Group.objects.get(name='Estudiantes')
        except Group.DoesNotExist:
            perfil1 = Group.objects.create(name='Estudiantes')
            perfil2 = Group.objects.create(name='Profesores')
            perfil3 = Group.objects.create(name='Director')
            perfil4 = Group.objects.create(name='Administrativos')

        instance.user.groups.add(perfil1)
