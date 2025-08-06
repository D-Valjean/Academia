import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.models import Group
from .forms import RegisterForm, UserForm, ProfileForm, CourseForm, UserCreationForm
from django.views import View
from .models import Course, Registration, Mark, Attendance, Notifications
from django.contrib.auth.models import User
from accounts.models import Profile
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
import pyjokes
from django.utils import timezone
from datetime import timedelta
# FUNCION PARA CONVERTIR EL PLURAL DE UN GRUPO A SU SINGULAR


def plural_to_singular(plural):
    # Diccionario de palabras
    plural_singular = {
        "estudiantes": "estudiante",
        "profesores": "profesor",
        "director": "director",
        "administrativos": "administrativo",
    }

    return plural_singular.get(plural, "error")


def time_passed(fecha):
    ahora = timezone.now()
    diferencia = ahora - fecha
    if diferencia < timedelta(minutes=1):
        return "hace unos segundos"
    elif diferencia < timedelta(hours=1):
        minutos = int(diferencia.total_seconds() // 60)
        return f"hace {minutos} minuto{'s' if minutos != 1 else ''}"
    elif diferencia < timedelta(days=1):
        horas = int(diferencia.total_seconds() // 3600)
        return f"hace {horas} hora{'s' if horas != 1 else ''}"
    else:
        dias = diferencia.days
        return f"hace {dias} día{'s' if dias != 1 else ''}"


def start_course():
    courses = Course.objects.filter(status='I')
    for course in courses:
        if course.start_date <= timezone.now().date():
            print(f"Empezando curso: {course.name}")
            course.status = 'P'
            course.save()


def end_course():
    courses = Course.objects.filter(status="P")
    for course in courses:
        if course.end_date is not None and course.end_date <= timezone.now().date():
            print(f"Finalizando curso: {course.name}")
            course.status = 'F'
            course.save()
# OBTENER COLOR Y GRUPO DE UN USUARIO


def get_group_and_color(user):
    group = user.groups.first()
    group_id = None
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

        group_id = group.id
        group_name = group.name
        group_name_singular = plural_to_singular(group.name)

    return group_id, group_name, group_name_singular, color

# DECORADOR PERSONALIZADO


def add_group_name_to_context(view_class):
    original_dispatch = view_class.dispatch

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        group_id, group_name, group_name_singular, color = get_group_and_color(
            user)
        try:
            profesores = 0
            for user in User.objects.all():
                for profile in Profile.objects.all():
                    if profile.user == user:
                        if user.groups.first().name == 'profesores':
                            if profile.active == True:
                                profesores += 1
        except:
            profesores = 0
        try:
            estudiantes = 0
            for user in User.objects.all():
                for profile in Profile.objects.all():
                    if profile.user == user:
                        if user.groups.first().name == 'estudiantes':
                            if profile.active == True:
                                estudiantes += 1
        except:
            estudiantes = 0
        joke = pyjokes.get_joke(language='es', category='neutral')
        start_course()
        end_course()
        print(joke)
        context = {
            'group_name': group_name,
            'group_name_singular': group_name_singular,
            'color': color,
            'total_courses': Course.objects.exclude(status='F').count(),
            'profesores': profesores,
            'estudiantes': estudiantes,
            'dad_joke': f"Ahora un chiste: \n{joke}",
        }

        self.extra_context = context
        return original_dispatch(self, request, *args, **kwargs)

    view_class.dispatch = dispatch
    return view_class


@add_group_name_to_context
class HomeView(TemplateView):
    template_name = 'front/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user if self.request.user.is_authenticated and self.request.user.groups.first(
        ).name == 'estudiantes' else None
        teacher = self.request.user if self.request.user.is_authenticated and self.request.user.groups.first(
        ).name == 'profesores' else None
        director = self.request.user if self.request.user.is_authenticated and self.request.user.groups.first(
        ).name == 'director' else None
        courses = []
        notification = []
        if student:
            registrations = Registration.objects.filter(student=student)
            courses = [registration.course for registration in registrations]
            notification = Notifications.objects.filter(
                user=student,).order_by('-id')[:5]

        elif teacher:
            courses = Course.objects.filter(teacher=teacher)
            students = []
            notification = Notifications.objects.filter(
                user=teacher,).order_by('-id')[:5]
            for course in courses:
                registrations = Registration.objects.filter(course=course)
                mark = Mark.objects.filter(course=course)
                for registration in registrations:
                    for mark_item in mark:
                        if registration.student == mark_item.student:
                            students.append({
                                'student_name': registration.student.get_full_name(),
                                'student_average': mark_item.average if mark_item.average else 0,
                                'couse_name': course.name,
                            })
            students = sorted(
                students, key=lambda x: x['student_average'], reverse=True)
            # students = list(set(students))  # Eliminar duplicados
        elif director:
            courses = Course.objects.all()
            notification = Notifications.objects.filter(
                user=director,).order_by('-id')[:5]
            students = []
            for course in courses:
                registrations = Registration.objects.filter(course=course)
                for registration in registrations:
                    students.append(registration.student.get_full_name())
            students = list(set(students))
        for item in courses:
            item.is_enrolled = True
            enrollment_count = Registration.objects.filter(course=item).count()
            item.enrollment_count = enrollment_count
        for n in notification:
            n.time_passed = time_passed(n.created_at)

        context.update({
            'courses': courses,
            'notification': notification,
            'students': students if teacher else None,
        })
        return context


class RegisterView(View):
    def get(self, request):
        data = {
            'form': RegisterForm()
        }
        return render(request, 'registration/register.html', data)

    def post(self, request):
        user_creation_form = RegisterForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(username=user_creation_form.cleaned_data['username'],
                                password=user_creation_form.cleaned_data['password1'])
            login(request, user)

            # Actualizar el campo created_by_admin del modelo Profile
            user.profile.created_by_admin = False
            user.profile.save()

            return redirect('home')
        data = {
            'form': user_creation_form
        }
        return render(request, 'registration/register.html', data)

# PAGINA DE PERFIL


@add_group_name_to_context
class ProfileView(TemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_form'] = UserForm(instance=user)
        context['profile_form'] = ProfileForm(instance=user.profile)

        if user.groups.first().name == 'profesores':
            # Obtener todos los cursos asignados al profesor
            assigned_courses = Course.objects.filter(
                teacher=user).order_by('-id')
            inscription_courses = assigned_courses.filter(status='I')
            progress_courses = assigned_courses.filter(status='P')
            finalized_courses = assigned_courses.filter(status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'estudiantes':
            # Obtener todos los cursos donde esta inscripto el estudiante
            student_id = user.id
            registrations = Registration.objects.filter(student=user)
            enrolled_courses = []
            inscription_courses = []
            progress_courses = []
            finalized_courses = []

            for registration in registrations:
                course = registration.course
                enrolled_courses.append(course)

                if course.status == 'I':
                    inscription_courses.append(course)
                elif course.status == 'P':
                    progress_courses.append(course)
                elif course.status == 'F':
                    finalized_courses.append(course)

            context['student_id'] = student_id
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'director':
            # Obtener todos los cursos existentes
            all_courses = Course.objects.all()
            inscription_courses = all_courses.filter(status='I')
            progress_courses = all_courses.filter(status='P')
            finalized_courses = all_courses.filter(status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'administrativos':
            # Obtengo todos los usuarios que no pertenecen al grupo administrativos
            admin_group = Group.objects.get(name='administrativos')
            all_users = User.objects.exclude(groups__in=[admin_group])

            # Obtengo todos los grupos
            all_groups = Group.objects.all()

            # Obtengo cada perfil de usuario
            user_profile = []
            for user in all_users:
                profile = user.profile
                user_groups = user.groups.all()
                processed_groups = [plural_to_singular(
                    group.name) for group in user_groups]
                user_profile.append({
                    'user': user,
                    'groups': processed_groups,
                    'profile': profile
                })

            context['user_profiles'] = user_profile

            # Obtener todos los cursos existentes
            all_courses = Course.objects.all()
            inscription_courses = all_courses.filter(status='I')
            progress_courses = all_courses.filter(status='P')
            finalized_courses = all_courses.filter(status='F')
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
            # Redireccionar a la pagina de perfil (con datos actualizados)
            return redirect('profile')

        # Si alguno de los datos no es valido
        context = self.get_context_data()
        context['user_form'] = user_form
        context['profile_form'] = profile_form
        return render(request, 'profile/profile.html', context)

# MOSTRAR TODOS LOS CURSOS


@add_group_name_to_context
class CoursesView(TemplateView):
    template_name = 'cursos/courses.html'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener el parámetro de filtro de la URL
        status_filter = self.request.GET.get('status', 'all')

        # Obtener todos los cursos ordenados por ID descendente
        courses = Course.objects.all().order_by('-id')

        # Aplicar filtro por estado si no es 'all'
        if status_filter != 'all':
            courses = courses.filter(status=status_filter)

        # Paginación
        paginator = Paginator(courses, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        student = self.request.user if self.request.user.is_authenticated else None

        # Para cada curso en la página actual, verificar si el estudiante está inscrito y contar inscritos
        for item in page_obj:
            if student:
                registration = Registration.objects.filter(
                    course=item, student=student).first()
                item.is_enrolled = registration is not None
            else:
                item.is_enrolled = False

            enrollment_count = Registration.objects.filter(course=item).count()
            item.enrollment_count = enrollment_count
        context.update({
            'courses': page_obj,
            'status_filter': status_filter,
            'is_paginated': page_obj.has_other_pages(),
            'page_obj': page_obj,  # Para la paginación en la plantilla
            'student': student,
        })

        return context

# PAGINA DE ERROR DE ACCESO A PAGINA NO PERMITIDA


@add_group_name_to_context
class ErrorView(TemplateView):
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_image_path = os.path.join(settings.MEDIA_URL, 'error.png')
        context['error_image_path'] = error_image_path
        return context

# CREAR UN NUEVO CURSO


@add_group_name_to_context
class CourseCreateView(UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'cursos/create_course.html'
    success_url = reverse_lazy('courses')

    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        messages.success(
            self.request, 'El registro se ha guardado correctamente')
        notication = Notifications(
            user=form.instance.teacher,
            message=f'Se le ha asignado el curso: {form.instance.name}',
            status='A'
        )
        notication.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, 'Ha ocurrido un error al guardar el registro')
        return self.render_to_response(self.get_context_data(form=form))

# EDICION DE UN CURSO


@add_group_name_to_context
class CourseeditView(UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'cursos/edit_course.html'
    success_url = reverse_lazy('courses')

    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists() or self.request.user.groups.filter(name='director').exists()

    def handle_no_permission(self):
        return redirect('error')

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, 'El registro se ha actualizado satisfactoriamente')
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(
            self.request, 'Ha ocurrido un error al actualizar el registro')
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

# REGISTRO DE UN USUARIO EN UN CURSO


@add_group_name_to_context
class CourseEnrollmentView(TemplateView):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        if request.user.is_authenticated and request.user.groups.first().name == 'estudiantes':
            student = request.user

            # Verificar si el estudiante ya está inscrito
            if Registration.objects.filter(course=course, student=student).exists():
                messages.info(request, 'Ya estás inscrito en este curso.')
                return redirect('courses')

            enrollment_count = Registration.objects.filter(
                course=course).count()
            if course.status != 'I' or enrollment_count >= course.capacity:
                messages.error(
                    request, 'No se puede inscribir, el curso está lleno.')
                return redirect('courses')

            # Crear un registro de inscripción asociado al estudiante y el curso
            registration = Registration(course=course, student=student)
            registration.save()
            notification = Notifications(
                user=student, message=f'Te has inscrito en el curso: {course.name}', status='I')
            notification.save()
            # Actualizar el estado del curso si se alcanza la capacidad
            enrollment_count += 1
            if enrollment_count >= course.capacity:
                course.status = 'P'
                course.save()

            messages.success(request, 'Inscripción exitosa')
        else:
            messages.error(request, 'No se pudo completar la inscripción')

        return redirect('courses')

# MOSTRAR LISTA DE ALUMNOS Y NOTAS A LOS PROFESORES


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
            student = get_object_or_404(User, id=mark.student_id)
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

# ACTUALIZAR NOTAS DE ALUMNOS


@add_group_name_to_context
class UpdateMarkView(UpdateView):
    model = Mark
    fields = ['mark_1', 'mark_2', 'mark_3']
    template_name = 'update_mark.html'

    def get_success_url(self):
        return reverse_lazy('studentlist', kwargs={'course_id': self.object.course.id})

    def form_valid(self, form):
        response = super().form_valid(form)
        Notifications.objects.create(
            user=self.object.student,
            message=f'Tus notas han sido actualizadas en el curso: {self.object.course.name}, {self.object.marks},',
            status='N'
        )
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
        # para que de una vez ordene por orden de fecha en la pagina
        return Attendance.objects.filter(course_id=course_id, date__isnull=False).order_by('date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(id=self.kwargs['course_id'])
        students = Registration.objects.filter(course=course).values(
            'student__id', 'student__first_name', 'student__last_name', 'enabled')
        all_dates = Attendance.objects.filter(course=course, date__isnull=False).values_list(
            'date', flat=True).distinct().order_by('date')
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
                    total_attendance_false = Attendance.objects.filter(
                        student_id=student['student__id'], course=course, present=False).count()
                    absences_percent = (
                        total_attendance_false / course.class_quantity) * 100
                    if absences_percent > 20:
                        student['enabled'] = False
                    else:
                        student['enabled'] = True
                except Attendance.DoesNotExist:
                    attendance_status = False

                student_data = {
                    'student': student,
                    'attendance_status': attendance_status,
                    'enabled': student['enabled']
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
        context = super().get_context_data(**kwargs)
        course_id = kwargs['course_id']
        course = Course.objects.get(id=course_id)
        registrations = Registration.objects.filter(course=course)
        context['course'] = course
        context['registrations'] = registrations
        return context

    def post(self, request, course_id):
        date = request.POST.get('date')
        course = Course.objects.get(id=course_id)
        registrations = Registration.objects.filter(course=course)

        if Attendance.objects.filter(course=course, date=date).exists():
            # Aquí puedes manejar el caso cuando la fecha ya existe, por ejemplo, puedes mostrar un mensaje de error
            messages.error(request, 'La fecha ya existe para este curso.')
            return redirect('add_attendance', course_id=course_id)
        else:
            # Aquí puedes continuar con tu lógica si la fecha no existe en la base de datos
            for registration in registrations:
                present = request.POST.get(
                    'attendance_' + str(registration.student.id))
                attendance = Attendance.objects.filter(
                    student=registration.student, course=course, date=None).first()

                if attendance:
                    attendance.date = date
                    attendance.present = bool(present)
                    attendance.save()
                    attendance.update_registration_enabled_status()

        return redirect('list_attendance', course_id=course_id)

# CONSULTAR LA EVOLUCION DE UN ESTUDIANTE DADO


def evolution(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id)
    teacher = course.teacher.get_full_name()
    class_quantity = course.class_quantity
    student = student_id
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

# CAMBIAR LA CONTRASEÑA DEL USUARIO


@add_group_name_to_context
class ProfilePasswordChangeView(PasswordChangeView):
    template_name = 'profile/change_password.html'
    success_url = reverse_lazy('profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_changed'] = self.request.session.get(
            'password_changed', False)
        return context

    def form_valid(self, form):
        # Actualizar el campo created_by_admin del modelo Profile
        profile = Profile.objects.get(user=self.request.user)
        profile.created_by_admin = False
        profile.save()

        messages.success(self.request, 'Cambio de contraseña exitoso')
        update_session_auth_hash(self.request, form.user)
        self.request.session['password_changed'] = True
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Hubo un error al momento de intentar cambiar la contraseña: {}.'.format(
                form.errors.as_text()
            )
        )
        return super().form_invalid(form)

# AGREGAR UN NUEVO USUARIO


@add_group_name_to_context
class AddUserView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
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

# LOGIN PERSONALIZADO


@add_group_name_to_context
class CustomloginView(LoginView):
    def form_valid(self, form):
        # Acceder al perfil del usuario
        profile = form.get_user().profile
        if not profile.active:
            messages.error(
                self.request, 'Tu cuenta ha sido desactivada. Contacta al administrador.')
            return redirect('login')
        # Verificamos el valor del campo created_by_admin
        response = super().form_valid(form)
        if profile.created_by_admin:
            messages.info(
                self.request, 'BIENVENIDO, Cambie su contraseña ahora !!!')
            response['Location'] = reverse_lazy('profile_password_change')
            response.status_code = 302

        return response

    def get_success_url(self):
        return super().get_success_url()

# VISUALIZACION DEL PERFIL DE UN USUARIO


@add_group_name_to_context
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user_detail.html'
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        group_id, group_name, group_name_singular, color = get_group_and_color(
            user)

        # Obtengo todos los grupos
        groups = Group.objects.all()
        singular_names = [plural_to_singular(
            group.name).capitalize() for group in groups]
        groups_ids = [group.id for group in groups]
        singular_groups = zip(singular_names, groups_ids)
        context['group_id_user'] = group_id
        context['group_name_user'] = group_name
        context['group_name_singular_user'] = group_name_singular
        context['color_user'] = color
        context['singular_groups'] = singular_groups

        if user.groups.first().name == 'profesores':
            # Obtener todos los cursos asignados al profesor
            assigned_courses = Course.objects.filter(
                teacher=user).order_by('-id')
            inscription_courses = assigned_courses.filter(status='I')
            progress_courses = assigned_courses.filter(status='P')
            finalized_courses = assigned_courses.filter(status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'estudiantes':
            # Obtener todos los cursos donde esta inscripto el estudiante
            student_id = user.id
            registrations = Registration.objects.filter(student=user)
            enrolled_courses = []
            inscription_courses = []
            progress_courses = []
            finalized_courses = []

            for registration in registrations:
                course = registration.course
                enrolled_courses.append(course)

                if course.status == 'I':
                    inscription_courses.append(course)
                elif course.status == 'P':
                    progress_courses.append(course)
                elif course.status == 'F':
                    finalized_courses.append(course)

            context['student_id'] = student_id
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'director':
            # Obtener todos los cursos existentes
            all_courses = Course.objects.all()
            inscription_courses = all_courses.filter(status='I')
            progress_courses = all_courses.filter(status='P')
            finalized_courses = all_courses.filter(status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses
        return context

# GRABACION DE LOS DATOS DE UN USUARIO


def super_user_edit(request, user_id):
    if not request.user.is_superuser:
        return redirect('error')

    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=user.profile)
        group = request.POST.get('group')

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            user.groups.clear()
            user.groups.add(group)
            return redirect('user_detail', pk=user.id)
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'profile/user_details.html', context)
