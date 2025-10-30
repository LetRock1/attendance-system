from django.db import transaction
from django.db.models import Count, Q
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from .models import AttendanceRecord, AttendanceSession, Student, Classroom

class AttendanceService:
    """Service class for attendance-related business logic"""
    
    @staticmethod
    @transaction.atomic
    def mark_attendance(session_id, present_student_ids):
        """
        Mark attendance for a session
        Args:
            session_id: ID of the attendance session
            present_student_ids: List of student IDs marked as present
        """
        try:
            session = AttendanceSession.objects.get(pk=session_id)
            class_students = session.classroom.students.all()
            
            # Create or update attendance records
            for student in class_students:
                status = student.studId in present_student_ids
                AttendanceRecord.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={'status': status}
                )
            
            return True, "Attendance marked successfully"
        except AttendanceSession.DoesNotExist:
            return False, "Session not found"
        except Exception as e:
            return False, f"Error marking attendance: {str(e)}"
    
    @staticmethod
    def get_attendance_percentage(student, classroom):
        """
        Calculate attendance percentage for a student in a specific class
        Args:
            student: Student object
            classroom: Classroom object
        Returns:
            float: Attendance percentage
        """
        try:
            # Get all sessions for this class
            sessions = AttendanceSession.objects.filter(classroom=classroom)
            total_sessions = sessions.count()
            
            if total_sessions == 0:
                return 0.0
            
            # Count present records
            present_count = AttendanceRecord.objects.filter(
                session__classroom=classroom,
                student=student,
                status=True
            ).count()
            
            percentage = (present_count / total_sessions) * 100
            return round(percentage, 2)
        except Exception as e:
            return 0.0

class ReportGenerator:
    """Service class for report generation business logic"""
    
    @staticmethod
    def get_defaulter_list(classroom_id, threshold=75.0):
        """
        Get list of students below attendance threshold
        Args:
            classroom_id: ID of the college class
            threshold: Minimum attendance percentage required
        Returns:
            tuple: (classroom, list of defaulters with percentages)
        """
        try:
            classroom = Classroom.objects.get(pk=classroom_id)
            students = classroom.students.all()
            defaulters = []
            
            for student in students:
                percentage = AttendanceService.get_attendance_percentage(student, classroom)
                if percentage < threshold:
                    defaulters.append({
                        'student': student,
                        'percentage': percentage
                    })
            
            return classroom, defaulters
        except Classroom.DoesNotExist:
            return None, []
    
    @staticmethod
    def generate_attendance_pdf_for_session(session_id):
        """
        Generate PDF report for a specific attendance session
        Args:
            session_id: ID of the attendance session
        Returns:
            BytesIO: PDF file in memory buffer
        """
        try:
            session = AttendanceSession.objects.get(pk=session_id)
            records = AttendanceRecord.objects.filter(session=session).select_related('student')
            
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            
            # Set up PDF content
            pdf.setTitle(f"Attendance Report - {session}")
            
            # Header
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawString(1 * inch, 10 * inch, "Attendance Management System")
            pdf.setFont("Helvetica", 12)
            pdf.drawString(1 * inch, 9.7 * inch, f"Class: {session.classroom.className}")
            pdf.drawString(1 * inch, 9.4 * inch, f"Subject: {session.classroom.subject.subName}")
            pdf.drawString(1 * inch, 9.1 * inch, f"Date: {session.date}")
            pdf.drawString(1 * inch, 8.8 * inch, f"Time: {session.startTime} - {session.endTime}")
            
            # Table header
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(1 * inch, 8.4 * inch, "Student ID")
            pdf.drawString(2.5 * inch, 8.4 * inch, "Student Name")
            pdf.drawString(5 * inch, 8.4 * inch, "Status")
            
            # Table content
            pdf.setFont("Helvetica", 10)
            y_position = 8.1 * inch
            for record in records:
                if y_position < 1 * inch:  # New page if needed
                    pdf.showPage()
                    y_position = 10 * inch
                
                pdf.drawString(1 * inch, y_position, record.student.studKey)
                pdf.drawString(2.5 * inch, y_position, record.student.name)
                status = "Present" if record.status else "Absent"
                pdf.drawString(5 * inch, y_position, status)
                y_position -= 0.3 * inch
            
            pdf.save()
            buffer.seek(0)
            return buffer
        except AttendanceSession.DoesNotExist:
            return None