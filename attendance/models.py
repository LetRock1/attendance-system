from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

class Department(models.Model):
    deptId = models.AutoField(primary_key=True)
    deptName = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.deptName
    
    class Meta:
        db_table = 'department_list'

class Subject(models.Model):
    subId = models.AutoField(primary_key=True)
    subName = models.CharField(max_length=100)
    credits = models.IntegerField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.subName
    
    class Meta:
        db_table = 'subjects_list'

class Student(models.Model):
    studId = models.AutoField(primary_key=True)
    studKey = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.studKey})"
    
    class Meta:
        db_table = 'student_list'

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    class Meta:
        db_table = 'teacher_list'

class Classroom(models.Model): 
    YEAR_CHOICES = [
        ('2024-25', '2024-25'),
        ('2025-26', '2025-26'),
        ('2026-27', '2026-27'),
    ]
    
    SEMESTER_CHOICES = [
        ('Sem I', 'Semester I'),
        ('Sem II', 'Semester II'),
        ('Sem III', 'Semester III'),
        ('Sem IV', 'Semester IV'),
        ('Sem V', 'Semester V'),
        ('Sem VI', 'Semester VI'),
    ]
    
    classId = models.AutoField(primary_key=True)
    className = models.CharField(max_length=50)
    year = models.CharField(max_length=7, choices=YEAR_CHOICES)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)
    
    def __str__(self):
        return f"{self.className} - {self.subject.subName}"
    
    class Meta:
        db_table = 'classroom_list'

class AttendanceSession(models.Model):
    sessionId = models.AutoField(primary_key=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)  # FIXED: Changed 'classroom' to 'Classroom'
    date = models.DateField()
    startTime = models.TimeField()
    endTime = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    def clean(self):
        if self.endTime <= self.startTime:
            raise ValidationError("End time must be after start time")
    
    def is_current(self):
        """Check if session is for today and hasn't ended yet"""
        import datetime
        from django.utils import timezone
        today = timezone.now().date()
        current_time = timezone.now().time()
        # Session is "current" if it's today and hasn't ended yet
        return (self.date == today and current_time <= self.endTime)
    
    def __str__(self):
        return f"{self.classroom.className} - {self.date}"
    
    class Meta:
        db_table = 'attendance_session'

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        (True, 'Present'),
        (False, 'Absent'),
    ]
    
    recordId = models.AutoField(primary_key=True)
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.BooleanField(choices=STATUS_CHOICES, default=False)
    
    class Meta:
        db_table = 'attendance_record'
        unique_together = ['session', 'student']
    
    def __str__(self):
        status = "Present" if self.status else "Absent"
        return f"{self.student.name} - {status}"