from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import TemplateView
from django.contrib.auth.models import Group
from .forms import RegisterForm
from django.views import View
# Create your views here.


class CustumTemplateView(TemplateView):
    group_name = None

    def get_contex_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ruser = self.request.user  # ruser = request.user from the request
        group_name = None
        if ruser.is_authenticated:
            group = Group.objects.filter(user=ruser).first()
            if group:
                group_name = group.name
        context['group_name'] = group_name
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
