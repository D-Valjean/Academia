from django.urls import path
from .views import HomeView, RegisterView, ProfileView, CoursesView, CourseCreateView, ErrorView, CourseeditView, CourseDeleteView, CourseEnrollmentView, StudentlistMarkView, UpdateMarkView, AttendanceListView, AddAttendanceView, evolution, ProfilePasswordChangeView, AddUserView, CustomloginView, UserDetailView, super_user_edit
# esto es para proteger las rutas de la web para que usuarios no autorizados no puedan acceder
from django.contrib.auth.decorators import login_required
from django.conf import settings

urlpatterns = [
    # PAGINA DE INICIO
    path('', HomeView.as_view(), name='home'),
    # PAGINAS DE LOGIN Y REGISTRO (VIDEO 5)
    path('register/', RegisterView.as_view(), name='register'),

    # PAGINAS DE PERFIL: VISTA DE PERFIL - EDICION DEL PERFIL (VIDEO 8)
    path('profile/', login_required(ProfileView.as_view()), name='profile'),

    # PAGINAS QUE ADMINISTRAN LOS CURSOS: LA LISTA DE CURSOS - (LA CREACION DE CURSOS - LA EDICION DE CURSOS - LA ELIMINACION DE CURSOS) (VIDEO 10)
    path('courses/', CoursesView.as_view(), name='courses'),
    path('courses/create/', login_required(CourseCreateView.as_view()),
         name='course_create'),
    path('courses/<int:pk>/edit/',
         login_required(CourseeditView.as_view()), name='course_edit'),
    path('courses/<int:pk>/delete/',
         login_required(CourseDeleteView.as_view()), name='course_delete'),

    # INSCRIPCION DE UN ALUMNO EN UN CURSO
    path('enroll_course/<int:course_id>',
         login_required(CourseEnrollmentView.as_view()), name='enroll_course'),
    path('error/', login_required(ErrorView.as_view()), name='error'),

    # PAGINA DE VISTA DE INSCRIPCION

    # PAGINAS ADMINISTRACION DE NOTAS: (LISTA DE ESTUDIANTES POR CURSO - EDICION DE NOTAS)
    path('courses/<int:course_id>',
         login_required(StudentlistMarkView.as_view()), name='studentlist'),
    path('courses/update_mark/<int:mark_id>',
         login_required(UpdateMarkView.as_view()), name='update_mark'),

    # PAGINAS DE ASISTENCIAS: (LISTA DE ESTUDIANTES POR CURSO - AGREGAR ASISTENCIAS)
    path('course/<int:course_id>/list_attendance/',
         login_required(AttendanceListView.as_view()), name='list_attendance'),
    path('course/<int:course_id>/add_attendance/',
         login_required(AddAttendanceView.as_view()), name='add_attendance'),

    # EVOLUCION DEL ESTUDIANTE
    path('evolution/<int:course_id>/<int:student_id>/',
         login_required(evolution), name='evolution'),

    # CAMBIO DE CONTRASEÑA
    path('password_change/', login_required(ProfilePasswordChangeView.as_view()),
         name='profile_password_change'),

    # AGREGAR NUEVO USUARIO
    path('add_user/', AddUserView.as_view(), name='add_user'),

    # NUEVO LOGIN
    path('login/', CustomloginView.as_view(), name='custom_login'),

    # VISUALIZAR EL PERFIL DE UN USUARIO
    path('user_details/<int:pk>/', UserDetailView.as_view(), name='user_detail'),

    # EDITAR DATOS DEL USUARIO
    path('super_user_edit/<int:user_id>/',
         login_required(super_user_edit), name='super_user_edit'),
]
