from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from accounts.models import Profile
from .models import Course
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit


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

    def clean_email(self):
        email_field = self.cleaned_data['email']

        if User.objects.filter(email=email_field).exists():
            raise forms.ValidationError(
                'Este correo electrónico ya está registrado')

        return email_field


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'address', 'location', 'telephone']


class CourseForm(forms.ModelForm):
    teacher = forms.ModelChoiceField(queryset=User.objects.filter(
        groups__name='profesores'), label='Profesor')
    status = forms.ChoiceField(
        choices=Course.STATUS_CHOICES, initial='I', label='Estado')
    description = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 3}), label='Descripción')
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), label='Fecha de inicio', required=False)
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}), label='Fecha de finalización', required=False)

    class Meta:
        model = Course
        fields = ['name', 'description', 'teacher',
                  'class_quantity', 'status', 'start_date', 'end_date']

    helper = FormHelper()
    helper.layout = Layout(
        Field('name'),
        Field('description'),
        Field('teacher'),
        Field('class_quantity'),
        Field('status'),
        Field('start_date'),
        Field('end_date'),
        Submit('submit', 'Submit')
    )


class UserCreationform(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
