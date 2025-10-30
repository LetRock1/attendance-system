from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Redirect root URL to login page
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/students/', views.StudentAPIView.as_view(), name='student-api'),
    
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Student CRUD
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('students/create/', views.StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/update/', views.StudentUpdateView.as_view(), name='student-update'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student-delete'),
    
    # Teacher CRUD
    path('teachers/', views.TeacherListView.as_view(), name='teacher-list'),
    path('teachers/create/', views.TeacherCreateView.as_view(), name='teacher-create'),
    path('teachers/<int:pk>/update/', views.TeacherUpdateView.as_view(), name='teacher-update'),
    path('teachers/<int:pk>/delete/', views.TeacherDeleteView.as_view(), name='teacher-delete'),
    
    # Department CRUD
    path('departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department-create'),
    path('departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department-update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department-delete'),
    
    # Subject CRUD
    path('subjects/', views.SubjectListView.as_view(), name='subject-list'),
    path('subjects/create/', views.SubjectCreateView.as_view(), name='subject-create'),
    path('subjects/<int:pk>/update/', views.SubjectUpdateView.as_view(), name='subject-update'),
    path('subjects/<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='subject-delete'),
    
    # Class CRUD
    path('classes/', views.ClassroomListView.as_view(), name='class-list'),
    path('classes/create/', views.ClassroomCreateView.as_view(), name='class-create'),
    path('classes/<int:pk>/update/', views.ClassroomUpdateView.as_view(), name='class-update'),
    path('classes/<int:pk>/delete/', views.ClassroomDeleteView.as_view(), name='class-delete'),
    
    # Session CRUD
    path('sessions/', views.AttendanceSessionListView.as_view(), name='session-list'),
    path('sessions/create/', views.AttendanceSessionCreateView.as_view(), name='session-create'),
    path('sessions/<int:pk>/update/', views.AttendanceSessionUpdateView.as_view(), name='session-update'),
    path('sessions/<int:pk>/delete/', views.AttendanceSessionDeleteView.as_view(), name='session-delete'),
    
    # Teacher Features
    path('mark-attendance/<int:session_id>/', views.MarkAttendanceView.as_view(), name='mark-attendance'),
    
    # Reports
    path('reports/', views.ReportDashboardView.as_view(), name='report-dashboard'),
    path('reports/defaulters/', views.DefaulterReportView.as_view(), name='defaulter-report'),
    path('reports/attendance-pdf/', views.AttendancePDFView.as_view(), name='attendance-pdf'),
]