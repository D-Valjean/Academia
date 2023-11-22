from django.urls import path
from .views import HomeView, PricingView, RegisterView, ProfileView, CoursesView, CourseCreateView, ErrorView, CourseeditView, CourseDeleteView, CourseEnrollmentView, StudentlistMarkView, UpdateMarkView, AttendanceListView, AddAttendanceView, evolution
# esto es para proteger las rutas de la web para que usuarios no autorizados no puedan acceder
from django.contrib.auth.decorators import login_required
from django.conf import settings
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('pricing/', PricingView.as_view(), name='pricing'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', login_required(ProfileView.as_view()), name='profile'),
    path('courses/', CoursesView.as_view(), name='courses'),
    path('courses/create/', login_required(CourseCreateView.as_view()),
         name='courses_create'),
    path('courses/<int:pk>/edit/',
         login_required(CourseeditView.as_view()), name='course_edit'),
    path('courses/<int:course_id>/studentlist/', login_required(StudentlistMarkView.as_view()),
         name='studentlist'),
    path('courses/<int:pk>/delete/',
         login_required(CourseDeleteView.as_view()), name='course_delete'),
    path('enroll_course/<int:course_id>',
         CourseEnrollmentView.as_view(), name='enroll_course'),
    path('error/', login_required(ErrorView.as_view()), name='error'),
    path('courses/update_mark/<int:mark_id>',
         login_required(UpdateMarkView.as_view()), name='update_mark'),
    path('courses/<int:course_id>/attendance/',
         login_required(AttendanceListView.as_view()), name='list_attendance'),
    path('courses/<int:course_id>/attendance/add/',
         login_required(AddAttendanceView.as_view()), name='add_attendance'),
    # evolucion del estudiante
    path('evolution/<int:course_id>/', login_required(evolution), name='evolution'),]
