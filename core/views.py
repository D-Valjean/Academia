from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.models import Group
from .forms import RegisterForm, UserForm, ProfileForm, CourseForm
from django.views import View
from django.utils.decorators import method_decorator
from .forms import RegisterForm, ProfileForm, UserForm
from django.utils.decorators import method_decorator
from .models import Course, Registration, Attendance, Mark
from django.urls import reverse_lazy
from django.contrib import messages
# Create your views here.


def plural_to_singular(plural):
    # Diccionario de palabras
    plural_singular = {
        "estudiantes": "estudiante",
        "profesores": "profesor",
        "director": "director",
        "administrativos": "administrativo",
    }

    return plural_singular.get(plural, "error")


def add_group_name_to_context(view_class):
    original_dispatch = view_class.dispatch

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        group = user.groups.first()
        group_name = None
        group_name_singular = None
        color = None
        if group:
            if group.name == 'estudiantes':
                color = 'bg-primary'
            elif group.name == 'profesores':
                color = 'bg-success'
            elif group.name == 'director':
                color = 'bg-secondary'
            elif group.name == 'administrativos':
                color = 'bg-info'

            group_name = group.name
            group_name_singular = plural_to_singular(group.name)
        context = {
            'group_name': group_name,
            'group_name_singular': group_name_singular,
            'color': color
        }
        self.extra_context = context
        return original_dispatch(self, request, *args, **kwargs)

    view_class.dispatch = dispatch
    return view_class


# class CustumTemplateView(TemplateView):
#     group_name = None
#     group_name_singular = None
#     color = None

#     def get_contex_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.request.user  # ruser = request.user from the request
#         if user.is_authenticated:
#             group = Group.objects
#             if group:
#                 if group.name == 'estudiantes':
#                     self.color = 'bg-primary'
#                 elif group.name == 'profesores':
#                     self.color = 'bg-success'
#                 elif group.name == 'director':
#                     self.color = 'bg-secondary'
#                 elif group.name == 'administrativos':
#                     self.color = 'bg-danger'

#                 self.group_name = group.name
#                 self.group_name_singular = plural_to_singular(group.name)
#         context['group_name'] = self.group_name
#         context['group_name_singular'] = self.group_name_singular
#         context['color'] = self.color

#         return context

@add_group_name_to_context
class HomeView(TemplateView):
    template_name = 'home.html'


@add_group_name_to_context
class PricingView(TemplateView):
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
@add_group_name_to_context
class ProfileView(TemplateView):
    template_name = 'Profile/profile.html'

    def get_context_data(self, **kwargs):  # Jalar data de accounts
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_form'] = UserForm(instance=user)
        context['profile_form'] = ProfileForm(instance=user.profile)

        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            return redirect('profile')

        contex = self.get_context_data()
        contex['user_form'] = user_form
        contex['profile_form'] = profile_form
        return render(request, 'Profile/profile.html', contex)


# Mostrar Cursos
@add_group_name_to_context
class CoursesView(TemplateView):
    template_name = 'courses.html'

    def get_context_data(self, **kwargs):  # Jalar data de accounts
        context = super().get_context_data(**kwargs)
        courses = Course.objects.all()
        # color = None
        student = self.request.user if self.request.user.is_authenticated else None
        for item in courses:
            if student:
                registration = Registration.objects.filter(
                    course=item, student=student).first()
                item.is_enrolled = registration is not None
            else:
                item.is_enrolled = False
            enrollment_count = Registration.objects.filter(
                course=item).count()
            item.enrollment_count = enrollment_count
        # if courses.status == 'I':
        #     color = 'bg-success'
        # elif courses.status == 'P':
        #     color = 'bg-warning'
        # elif courses.status == 'F':
        #     color = 'bg-danger'
        context['courses'] = courses
        return context  # con esto ya tenemos todos los cursos de la base de datos


# Crear Cursos
@add_group_name_to_context
class CourseCreateView(CreateView):
    model = Course  # Definir el modelo el cual va trabajar
    form_class = CourseForm
    template_name = 'create_course.html'
    # Redireccionar a la pagina de cursos
    success_url = reverse_lazy('courses')

    def form_valid(self, form):
        messages.success(self.request, 'Curso creado con exito')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el curso')
        return self.render_to_response(self.get_context_data(form=form))
