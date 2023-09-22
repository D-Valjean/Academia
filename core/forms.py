from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from accounts.models import Profile
from .models import Course
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field


class LoginForm(AuthenticationForm):
    pass


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellido')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'password1', 'password2']

# Validar que no se repita el correo electronico
    def clean_email(self):
        email_field = self.cleaned_data.get('email')
        if User.objects.filter(email=email_field).exists():
            raise forms.ValidationError(
                'El correo ya se encuentra registrado')
        return email_field


# Modulo para que el User pueda Modificar algunos campos de su perfil
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name',
                  'last_name']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile  # <-- Importar de accounts para que el usuario pueda modificar sus datos
        fields = ['image', 'address', 'location', 'telephone']


class CourseForm(forms.ModelForm):
    # los campos teacher y status son campos especiales que tenemos que definir antes para que podemas seleccionar al momento de crear un curso nuevo
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='profesores'), label='Profesor'
    )
    status = forms.ChoiceField(
        choices=Course.STATUS_CHOICES, initial='I', label='Estado'
    )
    # ajustar el tama;o del campo de descripcion
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), label='Descripción'
    )

    class Meta:
        model = Course
        fields = ['name', 'description', 'teacher', 'class_quantity', 'status']

    helper = FormHelper()
    helper.layout = Layout(
        Field('name'),
        Field('description'),
        Field('teacher'),
        Field('class_quantity'),
        Field('status'),
        Submit('submit', 'submit'),
    )
