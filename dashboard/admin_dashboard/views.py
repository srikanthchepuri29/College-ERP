from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from students.models import StudentProfile
from faculty.models import FacultyProfile
from academics.models import Department, Course, Subject, FeeRecord, TimetableSlot, Semester
from attendance.models import AttendanceRecord
from results.models import ExamSchedule, Result, ExamSubmission
import calendar
from datetime import datetime, date
from django.http import JsonResponse
import json

@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied. Admin portal only.")
        return redirect('home')
    
    # Core stats
    total_students = StudentProfile.objects.count()
    total_faculty = FacultyProfile.objects.count()
    total_depts = Department.objects.count()
    total_courses = Course.objects.count()
    
    # Active approval queues
    pending_students = CustomUser.objects.filter(role='STUDENT', is_approved=False).order_by('-date_joined')
    pending_faculty = CustomUser.objects.filter(role='FACULTY', is_approved=False).order_by('-date_joined')
    
    # Fee aggregation for charts
    total_fees_paid = FeeRecord.objects.filter(status='PAID').count()
    total_fees_unpaid = FeeRecord.objects.filter(status='UNPAID').count()
    total_fees_pending = FeeRecord.objects.filter(status='PENDING').count()
    
    # Attendance summary
    total_attendance_records = AttendanceRecord.objects.count()
    present_records = AttendanceRecord.objects.filter(status='PRESENT').count()
    attendance_rate = int((present_records / total_attendance_records * 100)) if total_attendance_records > 0 else 100

    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_depts': total_depts,
        'total_courses': total_courses,
        'pending_students': pending_students,
        'pending_faculty': pending_faculty,
        'fees_paid': total_fees_paid,
        'fees_unpaid': total_fees_unpaid,
        'fees_pending': total_fees_pending,
        'attendance_rate': attendance_rate,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def approve_user(request, user_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "Unauthorized action.")
        return redirect('home')
        
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f"Account for {user.username} has been approved.")
    return redirect('admin_dashboard')

@login_required
def reject_user(request, user_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "Unauthorized action.")
        return redirect('home')
        
    user = get_object_or_404(CustomUser, id=user_id)
    username = user.username
    user.delete()
    messages.warning(request, f"Account registration for {username} was rejected and removed.")
    return redirect('admin_dashboard')

# ----------------- CLASS SCHEDULING -----------------
@login_required
def admin_schedule(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    slots = TimetableSlot.objects.all().order_by('day_of_week', 'start_time')
    subjects = Subject.objects.all().order_by('code')
    days_choices = TimetableSlot.DAYS_OF_WEEK
    
    context = {
        'slots': slots,
        'subjects': subjects,
        'days_choices': days_choices,
    }
    return render(request, 'dashboard/admin_schedule.html', context)

@login_required
def add_schedule_slot(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        day_of_week = request.POST.get('day_of_week')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        classroom = request.POST.get('classroom')
        
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
            
            TimetableSlot.objects.create(
                subject=subject,
                day_of_week=int(day_of_week),
                start_time=start_time,
                end_time=end_time,
                classroom=classroom
            )
            messages.success(request, "Timetable slot added successfully.")
        except Exception as e:
            messages.error(request, f"Error adding slot: {str(e)}")
            
    return redirect('admin_schedule')

@login_required
def delete_schedule_slot(request, slot_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    slot = get_object_or_404(TimetableSlot, id=slot_id)
    slot.delete()
    messages.success(request, "Timetable slot deleted successfully.")
    return redirect('admin_schedule')


# ----------------- ATTENDANCE CALENDAR -----------------
@login_required
def admin_attendance(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    subjects = Subject.objects.all().order_by('code')
    students = StudentProfile.objects.all().order_by('student_id')
    
    # Selected filters
    subject_id = request.GET.get('subject')
    student_id = request.GET.get('student')
    
    # Date variables
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    month_name = calendar.month_name[month]
    
    # Month list for dropdown selection
    months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years_list = range(today.year - 2, today.year + 3)
    
    # Generate Calendar Grid
    cal_grid = []
    attendance_dict = {}
    
    if subject_id and student_id:
        student = get_object_or_404(StudentProfile, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Get existing attendance records for the month
        records = AttendanceRecord.objects.filter(
            student=student,
            subject=subject,
            date__year=year,
            date__month=month
        )
        for r in records:
            attendance_dict[r.date.day] = r.status
            
        # Build raw month calendar using monthcalendar (weeks of days)
        raw_weeks = calendar.monthcalendar(year, month)
        
        for week in raw_weeks:
            week_days = []
            for day_idx, day_num in enumerate(week):
                if day_num == 0:
                    # Pad cell
                    week_days.append({
                        'day_num': '',
                        'is_weekend': False,
                        'status': '',
                        'date_str': ''
                    })
                else:
                    # Check if weekend (Saturday is idx 5, Sunday is idx 6)
                    is_weekend = (day_idx >= 5)
                    status = attendance_dict.get(day_num, 'UNMARKED')
                    date_str = f"{year:04d}-{month:02d}-{day_num:02d}"
                    week_days.append({
                        'day_num': day_num,
                        'is_weekend': is_weekend,
                        'status': status,
                        'date_str': date_str
                    })
            cal_grid.append(week_days)
            
    context = {
        'subjects': subjects,
        'students': students,
        'selected_subject_id': int(subject_id) if subject_id else None,
        'selected_student_id': int(student_id) if student_id else None,
        'selected_month': month,
        'selected_year': year,
        'month_name': month_name,
        'months_list': months_list,
        'years_list': years_list,
        'cal_grid': cal_grid,
    }
    return render(request, 'dashboard/admin_attendance.html', context)

@login_required
def save_attendance(request):
    if request.user.role not in ['ADMIN', 'FACULTY']:
        return JsonResponse({'status': 'error', 'message': 'Access denied.'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            subject_id = data.get('subject_id')
            date_str = data.get('date')
            status = data.get('status')
            
            # Parse Date
            record_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Weekend validation (weekday 5 is Saturday, 6 is Sunday)
            if record_date.weekday() >= 5:
                return JsonResponse({'status': 'error', 'message': 'Cannot mark attendance on weekend holidays.'}, status=400)
                
            student = get_object_or_404(StudentProfile, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            
            # Get or create record
            record, created = AttendanceRecord.objects.get_or_create(
                student=student,
                subject=subject,
                date=record_date,
                defaults={'status': status}
            )
            if not created:
                record.status = status
                record.save()
                
            return JsonResponse({'status': 'success', 'message': 'Attendance saved.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)


# ----------------- MARKS & RESULTS -----------------
@login_required
def admin_marks(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    subjects = Subject.objects.all().order_by('code')
    exams = ExamSchedule.objects.all().order_by('-date')
    
    # Selected filters
    exam_id = request.GET.get('exam')
    student_results = []
    selected_exam = None
    
    if exam_id:
        selected_exam = get_object_or_404(ExamSchedule, id=exam_id)
        # Find students enrolled in the course and semester of the subject
        subject = selected_exam.subject
        students = StudentProfile.objects.filter(course=subject.course, semester=subject.semester)
        
        # Build marks list
        for stud in students:
            result = Result.objects.filter(exam_schedule=selected_exam, student=stud).first()
            submission = ExamSubmission.objects.filter(exam_schedule=selected_exam, student=stud).first()
            student_results.append({
                'student': stud,
                'marks_obtained': result.marks_obtained if result else '',
                'grade': result.grade if result else '',
                'remarks': result.remarks if result else '',
                'has_record': result is not None,
                'submission': submission
            })
            
    context = {
        'subjects': subjects,
        'exams': exams,
        'selected_exam': selected_exam,
        'student_results': student_results,
    }
    return render(request, 'dashboard/admin_marks.html', context)

@login_required
def add_exam(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        subject_id = request.POST.get('subject')
        exam_type = request.POST.get('exam_type')
        date_str = request.POST.get('date')
        max_marks = request.POST.get('max_marks', 100)
        
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            exam_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            ExamSchedule.objects.create(
                name=name,
                subject=subject,
                exam_type=exam_type,
                date=exam_date,
                max_marks=int(max_marks)
            )
            messages.success(request, f"Exam '{name}' created successfully.")
        except Exception as e:
            messages.error(request, f"Error creating exam: {str(e)}")
            
    return redirect('admin_marks')

@login_required
def save_marks(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = get_object_or_404(ExamSchedule, id=exam_id)
        
        # Fetch enrolled students
        students = StudentProfile.objects.filter(course=exam.subject.course, semester=exam.subject.semester)
        
        try:
            for stud in students:
                marks = request.POST.get(f'marks_{stud.id}')
                grade = request.POST.get(f'grade_{stud.id}', '')
                remarks = request.POST.get(f'remarks_{stud.id}', '')
                
                if marks != '' and marks is not None:
                    result, created = Result.objects.get_or_create(
                        exam_schedule=exam,
                        student=stud,
                        defaults={
                            'marks_obtained': float(marks),
                            'grade': grade,
                            'remarks': remarks
                        }
                    )
                    if not created:
                        result.marks_obtained = float(marks)
                        result.grade = grade
                        result.remarks = remarks
                        result.save()
                else:
                    # Clear if empty
                    Result.objects.filter(exam_schedule=exam, student=stud).delete()
                    
            messages.success(request, "Student marks saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving marks: {str(e)}")
            
    return redirect(f'/dashboard/admin/marks/?exam={exam_id}')
