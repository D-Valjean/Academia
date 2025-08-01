from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuario')
    image = models.ImageField(
        default='default.png', upload_to='users/', verbose_name='Imagen de perfil')
    address = models.CharField(
        max_length=150, null=True, blank=True, verbose_name='Dirección')
    location = models.CharField(
        max_length=150, null=True, blank=True, verbose_name='Localidad')
    telephone = models.CharField(
        max_length=50, null=True, blank=True, verbose_name='Teléfono')
    created_by_admin = models.BooleanField(
        default=True, blank=True, null=True, verbose_name='Creado por el administrador')
    active = models.BooleanField(
        default=True, blank=True, null=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'
        ordering = ['-id']

    def str(self):
        return self.user.username


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
