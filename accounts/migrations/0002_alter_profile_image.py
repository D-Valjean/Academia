# Generated by Django 4.2.2 on 2023-09-16 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='users/default.png', upload_to='users/', verbose_name='Imagen de perfil'),
        ),
    ]
