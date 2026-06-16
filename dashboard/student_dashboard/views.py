from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from students.models import StudentProfile
from academics.models import Subject, TimetableSlot
from attendance.models import AttendanceRecord
from assignments.models import Assignment, AssignmentSubmission
from results.models import Result, ExamSchedule, ExamSubmission
from mcq_arena.models import QuizAttempt
import calendar
from datetime import date, datetime

@login_required
def student_dashboard(request):
    if request.user.role != 'STUDENT':
        messages.error(request, "Access denied. Student portal only.")
        return redirect('home')
        
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact the administrator.")
        return redirect('home')
        
    # Get subjects matching student course and semester
    subjects = Subject.objects.filter(course=profile.course, semester=profile.semester)
    
    # Calculate attendance percentages subject-wise
    attendance_data = []
    total_present = 0
    total_classes = 0
    for sub in subjects:
        total_sub_classes = AttendanceRecord.objects.filter(student=profile, subject=sub).count()
        present_sub_classes = AttendanceRecord.objects.filter(student=profile, subject=sub, status='PRESENT').count()
        percentage = int((present_sub_classes / total_sub_classes * 100)) if total_sub_classes > 0 else 100
        
        attendance_data.append({
            'subject': sub,
            'total': total_sub_classes,
            'present': present_sub_classes,
            'percentage': percentage
        })
        total_present += present_sub_classes
        total_classes += total_sub_classes
        
    overall_attendance = int((total_present / total_classes * 100)) if total_classes > 0 else 100
    
    # Get active/pending assignments
    all_assignments = Assignment.objects.filter(subject__in=subjects).order_by('-deadline')
    submitted_assignment_ids = AssignmentSubmission.objects.filter(student=profile).values_list('assignment_id', flat=True)
    pending_assignments = all_assignments.exclude(id__in=submitted_assignment_ids)
    
    # Get evaluated/submitted assignments
    graded_submissions = AssignmentSubmission.objects.filter(student=profile).order_by('-submitted_at')
    
    # Get exam results
    results = Result.objects.filter(student=profile).order_by('-exam_schedule__date')
    
    # Get completed quizzes count
    completed_quizzes_count = QuizAttempt.objects.filter(student=profile).count()
    
    context = {
        'profile': profile,
        'subjects': subjects,
        'attendance_data': attendance_data,
        'overall_attendance': overall_attendance,
        'pending_assignments': pending_assignments,
        'graded_submissions': graded_submissions,
        'results': results,
        'completed_quizzes_count': completed_quizzes_count,
    }
    return render(request, 'dashboard/student_dashboard.html', context)

@login_required
def submit_assignment(request, assignment_id):
    if request.user.role != 'STUDENT':
        messages.error(request, "Unauthorized action.")
        return redirect('home')
        
    student_profile = request.user.student_profile
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.method == 'POST' and request.FILES.get('submission_file'):
        file = request.FILES['submission_file']
        
        # Avoid duplicate submissions
        if AssignmentSubmission.objects.filter(assignment=assignment, student=student_profile).exists():
            messages.warning(request, "You have already uploaded a submission for this assignment.")
            return redirect('student_dashboard')
            
        try:
            # Create submission
            AssignmentSubmission.objects.create(
                assignment=assignment,
                student=student_profile,
                file=file
            )
            messages.success(request, f"Assignment '{assignment.title}' uploaded successfully.")
        except Exception as e:
            messages.error(request, f"Error uploading file: {str(e)}")
            
    return redirect('student_dashboard')

# ----------------- CLASS SCHEDULING -----------------
@login_required
def student_schedule(request):
    if request.user.role != 'STUDENT':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')
        
    slots = TimetableSlot.objects.filter(
        subject__course=profile.course, 
        subject__semester=profile.semester
    ).order_by('day_of_week', 'start_time')
    
    context = {
        'slots': slots,
    }
    return render(request, 'dashboard/student_schedule.html', context)


# ----------------- MARKS & RESULTS -----------------
@login_required
def student_marks(request):
    if request.user.role != 'STUDENT':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')
        
    results = Result.objects.filter(student=profile).order_by('-exam_schedule__date')
    
    context = {
        'results': results,
    }
    return render(request, 'dashboard/student_marks.html', context)

# ----------------- EXAMS & ATTEMPTS -----------------
@login_required
def student_exams(request):
    if request.user.role != 'STUDENT':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')
        
    exams_data = []
    exams = ExamSchedule.objects.filter(
        subject__course=profile.course, 
        subject__semester=profile.semester
    ).order_by('-date')
    
    for ex in exams:
        submission = ExamSubmission.objects.filter(exam_schedule=ex, student=profile).first()
        result = Result.objects.filter(exam_schedule=ex, student=profile).first()
        exams_data.append({
            'exam': ex,
            'submission': submission,
            'result': result,
            'is_submitted': submission is not None,
            'is_graded': result is not None
        })
        
    context = {
        'exams_data': exams_data,
    }
    return render(request, 'dashboard/student_exams.html', context)

@login_required
def submit_exam(request, exam_id):
    if request.user.role != 'STUDENT':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')
        
    exam = get_object_or_404(ExamSchedule, id=exam_id, subject__course=profile.course, subject__semester=profile.semester)
    
    if request.method == 'POST':
        answers = request.POST.get('answers')
        
        # Avoid duplicate submission
        if ExamSubmission.objects.filter(exam_schedule=exam, student=profile).exists():
            messages.warning(request, "You have already submitted answers for this exam.")
            return redirect('student_exams')
            
        try:
            ExamSubmission.objects.create(
                exam_schedule=exam,
                student=profile,
                answers=answers
            )
            messages.success(request, f"Exam '{exam.name}' has been submitted successfully.")
        except Exception as e:
            messages.error(request, f"Error submitting exam: {str(e)}")
            
    return redirect('student_exams')

@login_required
def student_attendance(request):
    if request.user.role != 'STUDENT':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')
        
    subjects = Subject.objects.filter(course=profile.course, semester=profile.semester).order_by('code')
    
    # Selected filters
    subject_id = request.GET.get('subject')
    
    # Date variables
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    month_name = calendar.month_name[month]
    months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years_list = range(today.year - 2, today.year + 3)
    
    cal_grid = []
    selected_subject = None
    
    if subject_id:
        selected_subject = get_object_or_404(Subject, id=subject_id, course=profile.course, semester=profile.semester)
        
        # Get existing attendance records for the month
        records = AttendanceRecord.objects.filter(
            student=profile,
            subject=selected_subject,
            date__year=year,
            date__month=month
        )
        attendance_dict = {}
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
        'selected_subject_id': int(subject_id) if subject_id else None,
        'selected_subject': selected_subject,
        'selected_month': month,
        'selected_year': year,
        'month_name': month_name,
        'months_list': months_list,
        'years_list': years_list,
        'cal_grid': cal_grid,
    }
    return render(request, 'dashboard/student_attendance.html', context)
