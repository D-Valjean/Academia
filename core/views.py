from django.db.models.query import QuerySet
from typing import Any
from django.db import models
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group, User
from .forms import RegisterForm, UserForm, ProfileForm, CourseForm, UserCreationform
from django.views import View
from django.utils.decorators import method_decorator
from .forms import RegisterForm, ProfileForm, UserForm
from django.utils.decorators import method_decorator
from .models import Course, Registration, Attendance, Mark
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.conf import settings
from datetime import datetime
from django.http import JsonResponse
import os
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
# Create your views here.


# Pasar al momento de ver en la aplicacion los grupos que se crearon en Django a singular
def plural_to_singular(plural):
    # Diccionario de palabras
    plural_singular = {
        "estudiantes": "estudiante",
        "profesores": "profesor",
        "director": "director",
        "administrativos": "administrativo",
    }

    return plural_singular.get(plural, "error")


# Esta funcion nos permite agregar el nombre del grupo al contexto,de esta forma no tenemos que validar el usuario en cada funcion, lo englobamos en uno sola
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

        if user.groups.first().name == 'profesores':
            # Obtener todos los cursos asignados al profesor
            assigned_courses = Course.objects.filter(
                teacher=user).order_by('-id')
            inscription_courses = assigned_courses.filter(
                status='I')
            progress_courses = assigned_courses.filter(
                status='P')
            finalized_courses = assigned_courses.filter(
                status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'estudiantes':
            # Obtener todos los cursos asignados al estudiante
            registration = Registration.objects.filter(
                student=user)
            enrolled_courses = []
            inscription_course = []
            progress_course = []
            finalized_courses = []
            for registration in registration:
                course = registration.course
                enrolled_courses.append(course)

                if course.status == 'I':
                    inscription_course.append(course)
                elif course.status == 'P':
                    progress_course.append(course)
                elif course.status == 'F':
                    finalized_courses.append(course)
            context['inscription_course'] = inscription_course
            context['progress_course'] = progress_course
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'director':
            # Obtener todos los cursos asignados al director
            all_courses = Course.objects.all()
            inscription_courses = all_courses.filter(
                status='I')
            progress_courses = all_courses.filter(
                status='P')
            finalized_courses = all_courses.filter(
                status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses
            # Obtener todos los cursos asignados al administrativo
        elif user.groups.first().name == 'administrativos':
            # Obtener todos los Usuarios
            all_user = User.objects.all()
            all_groups = Group.objects.all()
            user_profiles = []
            for user in all_user:
                profile = user.profile
                user_groups = user.groups.all()
                procesed_groups = [plural_to_singular(
                    group.name) for group in user_groups]  # Pasar a Singular
                user_profiles.append({
                    'user': user,
                    'groups': procesed_groups,
                    'profile': profile
                })
            context['user_profiles'] = user_profiles
            context['all_groups'] = all_groups

            # Obtener todos los cursos
            all_courses = Course.objects.all()
            inscription_courses = all_courses.filter(
                status='I')
            progress_courses = all_courses.filter(
                status='P')
            finalized_courses = all_courses.filter(
                status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

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
        courses = Course.objects.all().order_by('-id')
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


@add_group_name_to_context
class ErrorView(TemplateView):
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_image_path = os.path.join(settings.MEDIA_URL, 'error.webp')
        context['error_image_path'] = error_image_path
        return context


# Crear Cursos
@add_group_name_to_context
class CourseCreateView(UserPassesTestMixin, CreateView):
    model = Course  # Definir el modelo el cual va trabajar
    form_class = CourseForm
    template_name = 'create_course.html'
    # Redireccionar a la pagina de cursos
    success_url = reverse_lazy('courses')

    # Verificar si el usuario es administrativo y ningun otro tipo de usuario pueda acceder
    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect('error')

    def form_valid(self, form):
        messages.success(self.request, 'Curso creado con exito')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el curso')
        return self.render_to_response(self.get_context_data(form=form))


# Edicion de un curso
@add_group_name_to_context
class CourseeditView(UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'edit_course.html'
    # Redireccionar a la pagina de cursos
    success_url = reverse_lazy('courses')

    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()

    def handle_no_permission(self) -> HttpResponseRedirect:
        return redirect('error')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Curso editado con exito')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al editar el curso')
        return self.render_to_response(self.get_context_data(form=form))


# ELIMINACION DE UN REGISTRO
@add_group_name_to_context
class CourseDeleteView(UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'delete_course.html'
    success_url = reverse_lazy('courses')

    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        messages.success(
            self.request, 'El registro se ha eliminado correctamente')
        return super().form_valid(form)


# Registro de estudiante a curso
@add_group_name_to_context
class CourseEnrollmentView(TemplateView):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        if request.user.is_authenticated and request.user.groups.first().name == 'estudiantes':
            student = request.user

            registration = Registration(student=student, course=course)
            registration.save()

            messages.success(
                request, 'Se ha registrado el estudiante al curso')
        else:
            messages.error(
                request, 'No tienes permisos para realizar esta accion')
        return redirect('courses')


# Mostrar listas de alummnos y notas para profesores
@add_group_name_to_context
class StudentlistMarkView(TemplateView):
    template_name = 'student_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, id=course_id)
        marks = Mark.objects.filter(course=course)

        student_data = []
        for mark in marks:
            student = get_object_or_404(User, id=mark.student.id)
            student_data.append({
                'mark_id': mark.id,
                'name': student.get_full_name(),
                'mark_1': mark.mark_1,
                'mark_2': mark.mark_2,
                'mark_3': mark.mark_3,
                'average': mark.average,
            })
        context['course'] = course
        context['student_data'] = student_data
        return context


# Actualizar Notas de Alumnos
@add_group_name_to_context
class UpdateMarkView(UpdateView):
    model = Mark
    fields = ['mark_1', 'mark_2', 'mark_3']
    template_name = 'update_mark.html'

    def get_success_url(self):
        return reverse_lazy('studentlist', kwargs={'course_id': self.object.course.id})

    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mark = self.get_object()
        context['course_name'] = mark.course.name
        return context

    def get_object(self, queryset=None):
        mark_id = self.kwargs['mark_id']
        return get_object_or_404(Mark, id=mark_id)


@add_group_name_to_context
class AttendanceListView(ListView):
    model = Attendance
    template_name = 'attendance_list.html'

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Attendance.objects.filter(course_id=course_id, date__isnull=False).order_by('date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(id=self.kwargs['course_id'])
        students = Registration.objects.filter(course=course).values(
            'student__id', 'student__first_name', 'student__last_name', 'enable')

        all_dates = Attendance.objects.filter(
            course=course, date__isnull=False).values_list('date', flat=True).distinct()
        # [('2023-08-22'), ('2023-08-29')]
        # ('2023-08-22', '2023-08-29') => flat=True
        remaining_classes = course.class_quantity - all_dates.count()

        attendance_data = []

        for date in all_dates:
            attendance_dict = {
                'date': date,
                'attendance_data': []
            }

            for student in students:
                try:
                    attendance = Attendance.objects.get(
                        course=course, student_id=student['student__id'], date=date)
                    attendance_status = attendance.present
                except Attendance.DoesNotExist:
                    attendance_status = False

                student_data = {
                    'student': student,
                    'attendance_status': attendance_status,
                    'enable': student['enable']
                }

                attendance_dict['attendance_data'].append(student_data)

            attendance_data.append(attendance_dict)

        context['course'] = course
        context['students'] = students
        context['attendance_data'] = attendance_data
        context['remaining_classes'] = remaining_classes
        return context


@add_group_name_to_context
class AddAttendanceView(TemplateView):
    template_name = 'add_attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # Jalo los falta a una variable
        # Se crea una variable con espacio para almacenar los datos
        course_id = kwargs['course_id']
        # Consulto en la traba couse todos los id, y los relaciono con course_id, que luego lo almaceno en la variable course
        course = Course.objects.get(id=course_id)
        # Consulto en registros todos los cursos en la base de tatos y lo relaciono con la variable course que arriba
        registrations = Registration.objects.filter(course=course)
        context['course'] = course
        context['registrations'] = registrations
        return context

    def post(self, request, course_id):
        course = Course.objects.get(id=course_id)
        registrations = Registration.objects.filter(course=course)

        if request.method == 'POST':
            date = request.POST.get('date')

            for registration in registrations:
                present = request.POST.get(
                    'attendance_' + str(registration.student.id))
                attendance = Attendance.objects.filter(
                    student=registration.student, course=course, date=None).first()

                if attendance:
                    attendance.date = date
                    attendance.present = bool(present)
                    attendance.save()
                    attendance.update_registration_enable_status()

        return redirect('list_attendance', course_id=course_id)

# CONSULTAR EVOLUCION DEL ESTUDIANTE


def evolution(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    teacher = course.teacher.get_full_name()
    class_quantity = course.class_quantity
    student = request.user
    registration_status = Registration.objects.filter(
        course=course, student=student).values('enabled').first()
    attendances = Attendance.objects.filter(course=course, student=student)
    marks = Mark.objects.filter(course=course, student=student)

    attendances_data = []
    marks_data = []
    evolution_data = {}

    attendances_data = [
        {
            'date': attendance.date.strftime('%d-%m-%Y'),
            'present': attendance.present
        }
        for attendance in attendances if attendance.date is not None
    ]

    marks_data = [
        {
            'mark_1': item.mark_1,
            'mark_2': item.mark_2,
            'mark_3': item.mark_3,
            'average': item.average
        }
        for item in marks
    ]

    evolution_data = {
        'registration_status': registration_status,
        'teacher': teacher,
        'classQuantity': class_quantity,
        'courseStatus': course.status,
        'courseName': course.name,
        'attendances': attendances_data,
        'marks': marks_data
    }

    return JsonResponse(evolution_data, safe=False)


# Cambiar Contrase;a
@add_group_name_to_context
class ProfilePasswordChangeView(PasswordChangeView):
    template_name = 'Profile/change_password.html'
    success_url = reverse_lazy('profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_changed'] = self.request.session.get(
            'password_changed', False)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Contraseña cambiada con exito')
        update_session_auth_hash(self.request, form.user)
        self.request.session['password_changed'] = True
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al cambiar la contraseña')
        return super().form_invalid(form)

# Agregar un Nuevo Usuaro


@add_group_name_to_context
class AddUserView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationform
    template_name = 'add_user.html'
    success_url = '/profile/'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('error')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = Group.objects.all()
        singular_groups = [plural_to_singular(
            group.name).capitalize() for group in groups]
        context['groups'] = zip(groups, singular_groups)
        return context

    def form_valid(self, form):
        # Obtener el grupo que seleccionó
        group_id = self.request.POST['group']
        group = Group.objects.get(id=group_id)

        # Crear usuario sin guardarlo aún
        user = form.save(commit=False)

        # Colocamos una contraseña por defecto -Aca podría ir la lógica para crear una contraseña aleatoria-
        user.set_password('contraseña')

        # Convertir a un usuario al staff
        if group_id != '1':
            user.is_staff = True

        # Creamos el usuario
        user.save()

        # Agregamos el usuario al grupo seleccionado
        user.groups.clear()
        user.groups.add(group)

        return super().form_valid(form)
