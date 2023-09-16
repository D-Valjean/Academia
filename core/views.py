from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import TemplateView
from django.contrib.auth.models import Group
from .forms import RegisterForm
from django.views import View
from django.utils.decorators import method_decorator
# Create your views here.


def plural_to_singular(plural):
    # Diccionario de palabras
    plural_singular = {
        'estudiantes': 'estudiante',
        'profesores': 'profesor',
        'director': 'director',
        'administrativos': 'administrativo'
    }

    return plural_singular.get(plural, "error")


class CustumTemplateView(TemplateView):
    group_name = None
    group_name_singular = None

    def get_contex_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user  # ruser = request.user from the request
        if user.is_authenticated:
            group = Group.objects
            if group:
                self.group_name = group.name
                self.group_name_singular = plural_to_singular(group.name)
        context['group_name'] = self.group_name
        context['group_name_singular'] = self.group_name_singular

        return context


class HomeView(CustumTemplateView):
    template_name = 'home.html'


class PricingView(CustumTemplateView):
    template_name = 'pricing.html'


# REGISTRO DE USUARIO

class RegisterView(View):
    def get(self, request):
        data = {
            'form': RegisterForm(),
            'title': 'REGISTRO DE USUARIO'
        }
        return render(request, 'registration/register.html', data)

    def post(self, request):
        user_creation_form = RegisterForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(username=user_creation_form.cleaned_data['username'],
                                password=user_creation_form.cleaned_data['password1'])
            login(request, user)
            return redirect('home')
        data = {
            'form': user_creation_form
        }
        return render(request, 'registration/register.html', data)


# Pagina de Perfil
class ProfileView(CustumTemplateView):
    template_name = 'Profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        return context
