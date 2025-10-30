from django import forms
from .models import *

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['studKey', 'name', 'email', 'phone', 'department']
        widgets = {
            'studKey': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'department': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),  # ADD THIS
        }

class TeacherForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Teacher
        fields = ['department']
        widgets = {
            'department': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }
    
    def save(self, commit=True):
        # Create User first
        user_data = {
            'username': self.cleaned_data['username'],
            'email': self.cleaned_data['email'],
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
        }
        
        user = User.objects.create_user(**user_data)
        user.set_password(self.cleaned_data['password'])
        user.save()
        
        # Create Teacher
        teacher = super().save(commit=False)
        teacher.user = user
        if commit:
            teacher.save()
        return teacher

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['deptName']
        widgets = {
            'deptName': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subName', 'credits', 'department']
        widgets = {
            'subName': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'credits': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'department': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

class ClassroomForm(forms.ModelForm):  # CHANGED FROM ClassroomForm
    class Meta:
        model = Classroom  # CHANGED FROM Classroom
        fields = ['className', 'year', 'semester', 'teacher', 'subject', 'department', 'students']
        widgets = {
            'className': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'year': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'semester': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'teacher': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'subject': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'department': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'students': forms.SelectMultiple(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['students'].queryset = Student.objects.filter(department_id=department_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['students'].queryset = self.instance.department.student_set.all()
        else:
            self.fields['students'].queryset = Student.objects.none()

class AttendanceSessionForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = ['classroom', 'date', 'startTime', 'endTime']
        widgets = {
            'classroom': forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'startTime': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'endTime': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }