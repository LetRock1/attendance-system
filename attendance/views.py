from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
from .models import *
from .services import AttendanceService, ReportGenerator
from .forms import *

class StudentAPIView(View):
    def get(self, request):
        department_id = request.GET.get('department_id')
        if department_id:
            students = Student.objects.filter(department_id=department_id)
            student_data = [
                {
                    'id': student.studId,
                    'name': student.name,
                    'studKey': student.studKey
                }
                for student in students
            ]
            return JsonResponse({'students': student_data})
        return JsonResponse({'students': []})

# Decorators for role-based access
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.is_staff:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# Base View Classes
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and not self.request.user.is_staff

# Authentication Views
class CustomLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'attendance/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'attendance/login.html', {'error': 'Invalid credentials'})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard Views
class DashboardView(View):
    @method_decorator(login_required)
    def get(self, request):
        if request.user.is_staff:
            # Admin dashboard
            context = {
                'students_count': Student.objects.count(),
                'teachers_count': Teacher.objects.count(),
                'classes_count': Classroom.objects.count(),
                'subjects_count': Subject.objects.count(),
            }
            return render(request, 'attendance/dashboard_admin.html', context)
        else:
            # Teacher dashboard - ONLY show current sessions
            try:
                teacher = Teacher.objects.get(user=request.user)
                today_sessions = AttendanceSession.objects.filter(
                    classroom__teacher=teacher,
                    date=timezone.now().date(),
                    is_active=True
                )
                
                # Filter only sessions that are currently active (within time range)
                current_sessions = []
                for session in today_sessions:
                    if session.is_current():
                        current_sessions.append(session)
                
                context = {
                    'sessions': current_sessions,
                    'teacher': teacher,
                }
                return render(request, 'attendance/dashboard_teacher.html', context)
            except Teacher.DoesNotExist:
                return redirect('logout')


# CRUD Views for Admin
class StudentListView(AdminRequiredMixin, View):
    def get(self, request):
        students = Student.objects.all()
        return render(request, 'attendance/student_list.html', {'students': students})

class StudentCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = StudentForm()
        return render(request, 'attendance/student_form.html', {'form': form})
    
    def post(self, request):
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student-list')
        return render(request, 'attendance/student_form.html', {'form': form})

class StudentUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        form = StudentForm(instance=student)
        return render(request, 'attendance/student_form.html', {'form': form})
    
    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student-list')
        return render(request, 'attendance/student_form.html', {'form': form})

class StudentDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        student.delete()
        return redirect('student-list')

class TeacherListView(AdminRequiredMixin, View):
    def get(self, request):
        teachers = Teacher.objects.all()
        return render(request, 'attendance/teacher_list.html', {'teachers': teachers})

class TeacherCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = TeacherForm()
        return render(request, 'attendance/teacher_form.html', {'form': form})
    
    def post(self, request):
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher-list')
        return render(request, 'attendance/teacher_form.html', {'form': form})

class TeacherUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        teacher = get_object_or_404(Teacher, pk=pk)
        form = TeacherForm(instance=teacher, initial={
            'first_name': teacher.user.first_name,
            'last_name': teacher.user.last_name,
            'username': teacher.user.username,
            'email': teacher.user.email,
        })
        return render(request, 'attendance/teacher_form.html', {'form': form})
    
    def post(self, request, pk):
        teacher = get_object_or_404(Teacher, pk=pk)
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher-list')
        return render(request, 'attendance/teacher_form.html', {'form': form})

class TeacherDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        teacher = get_object_or_404(Teacher, pk=pk)
        teacher.user.delete()
        return redirect('teacher-list')

class DepartmentListView(AdminRequiredMixin, View):
    def get(self, request):
        departments = Department.objects.all()
        return render(request, 'attendance/department_list.html', {'departments': departments})

class DepartmentCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = DepartmentForm()
        return render(request, 'attendance/department_form.html', {'form': form})
    
    def post(self, request):
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department-list')
        return render(request, 'attendance/department_form.html', {'form': form})

class DepartmentUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        form = DepartmentForm(instance=department)
        return render(request, 'attendance/department_form.html', {'form': form})
    
    def post(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department-list')
        return render(request, 'attendance/department_form.html', {'form': form})

class DepartmentDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        department.delete()
        return redirect('department-list')

class SubjectListView(AdminRequiredMixin, View):
    def get(self, request):
        subjects = Subject.objects.all()
        return render(request, 'attendance/subject_list.html', {'subjects': subjects})

class SubjectCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = SubjectForm()
        return render(request, 'attendance/subject_form.html', {'form': form})
    
    def post(self, request):
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject-list')
        return render(request, 'attendance/subject_form.html', {'form': form})

class SubjectUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        form = SubjectForm(instance=subject)
        return render(request, 'attendance/subject_form.html', {'form': form})
    
    def post(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject-list')
        return render(request, 'attendance/subject_form.html', {'form': form})

class SubjectDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        subject.delete()
        return redirect('subject-list')

class ClassroomListView(AdminRequiredMixin, View):
    def get(self, request):
        classes = Classroom.objects.all()
        return render(request, 'attendance/class_list.html', {'classes': classes})

class ClassroomCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = ClassroomForm()
        return render(request, 'attendance/class_form.html', {'form': form})
    
    def post(self, request):
        form = ClassroomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class-list')
        return render(request, 'attendance/class_form.html', {'form': form})

class ClassroomUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        classroom = get_object_or_404(Classroom, pk=pk)
        form = ClassroomForm(instance=classroom)
        return render(request, 'attendance/class_form.html', {'form': form})
    
    def post(self, request, pk):
        classroom = get_object_or_404(Classroom, pk=pk)
        form = ClassroomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            return redirect('class-list')
        return render(request, 'attendance/class_form.html', {'form': form})

class ClassroomDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        classroom = get_object_or_404(Classroom, pk=pk)
        classroom.delete()
        return redirect('class-list')

class AttendanceSessionListView(AdminRequiredMixin, View):
    def get(self, request):
        sessions = AttendanceSession.objects.all()
        return render(request, 'attendance/session_list.html', {'sessions': sessions})

class AttendanceSessionCreateView(AdminRequiredMixin, View):
    def get(self, request):
        form = AttendanceSessionForm()
        return render(request, 'attendance/session_form.html', {'form': form})
    
    def post(self, request):
        form = AttendanceSessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('session-list')
        return render(request, 'attendance/session_form.html', {'form': form})

class AttendanceSessionUpdateView(AdminRequiredMixin, View):
    def get(self, request, pk):
        session = get_object_or_404(AttendanceSession, pk=pk)
        form = AttendanceSessionForm(instance=session)
        return render(request, 'attendance/session_form.html', {'form': form})
    
    def post(self, request, pk):
        session = get_object_or_404(AttendanceSession, pk=pk)
        form = AttendanceSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            return redirect('session-list')
        return render(request, 'attendance/session_form.html', {'form': form})

class AttendanceSessionDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        session = get_object_or_404(AttendanceSession, pk=pk)
        session.delete()
        return redirect('session-list')

# Teacher Views
class MarkAttendanceView(TeacherRequiredMixin, View):
    def get(self, request, session_id):
        session = get_object_or_404(AttendanceSession, pk=session_id)
        
        # Check if session is still valid
        if not session.is_current():
            return render(request, 'attendance/error.html', {
                'error': 'This attendance session has expired. Attendance can only be marked during the session time.'
            })
        
        students = session.classroom.students.all()
        
        # Get existing attendance records
        existing_records = AttendanceRecord.objects.filter(session=session)
        present_students = [record.student.studId for record in existing_records if record.status]
        
        context = {
            'session': session,
            'students': students,
            'present_students': present_students,
        }
        return render(request, 'attendance/mark_attendance.html', context)
    
    def post(self, request, session_id):
        session = get_object_or_404(AttendanceSession, pk=session_id)
        
        # Check if session is still valid
        if not session.is_current():
            return render(request, 'attendance/error.html', {
                'error': 'This attendance session has expired. Attendance can only be marked during the session time.'
            })
        
        present_student_ids = [int(id) for id in request.POST.getlist('present_students')]
        success, message = AttendanceService.mark_attendance(session_id, present_student_ids)
        
        if success:
            # Deactivate session after attendance is marked
            session.is_active = False
            session.save()
            return redirect('dashboard')
        else:
            students = session.classroom.students.all()
            return render(request, 'attendance/mark_attendance.html', {
                'error': message, 
                'session': session,
                'students': students,
                'present_students': present_student_ids
            })

# Report Views
class ReportDashboardView(AdminRequiredMixin, View):
    def get(self, request):
        classes = Classroom.objects.all()
        sessions = AttendanceSession.objects.all()
        return render(request, 'attendance/report_dashboard.html', {
            'classes': classes,
            'sessions': sessions
        })

class DefaulterReportView(AdminRequiredMixin, View):
    def get(self, request):
        class_id = request.GET.get('class_id')
        threshold = float(request.GET.get('threshold', 75.0))
        
        if class_id:
            classroom, defaulters = ReportGenerator.get_defaulter_list(class_id, threshold)
            return render(request, 'attendance/defaulter_report.html', {
                'classroom': classroom,
                'defaulters': defaulters,
                'threshold': threshold
            })
        
        return redirect('report-dashboard')

class AttendancePDFView(AdminRequiredMixin, View):
    def get(self, request):
        session_id = request.GET.get('session_id')
        if session_id:
            pdf_buffer = ReportGenerator.generate_attendance_pdf_for_session(session_id)
            if pdf_buffer:
                response = HttpResponse(pdf_buffer, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
                return response
        
        return redirect('report-dashboard')