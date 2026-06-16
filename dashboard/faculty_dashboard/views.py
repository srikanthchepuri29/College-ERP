from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from faculty.models import FacultyProfile
from academics.models import Subject, TimetableSlot
from mcq_arena.models import Quiz, Question
from assignments.models import Assignment, AssignmentSubmission
from results.models import ExamSchedule, Result, ExamSubmission
from datetime import datetime, date
from django.utils import timezone
from students.models import StudentProfile
from attendance.models import AttendanceRecord
import calendar

@login_required
def faculty_dashboard(request):
    if request.user.role != 'FACULTY':
        messages.error(request, "Access denied. Faculty portal only.")
        return redirect('home')
        
    try:
        profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found. Please contact the administrator.")
        return redirect('home')
        
    # Get subjects taught by this faculty member
    subjects = Subject.objects.filter(faculty=profile)
    subjects_count = subjects.count()
    
    # Get quizzes created by this faculty member
    quizzes = Quiz.objects.filter(created_by=profile).order_by('-start_time')
    quizzes_count = quizzes.count()
    
    # Get assignments created
    assignments = Assignment.objects.filter(created_by=profile).order_by('-deadline')
    assignments_count = assignments.count()
    
    # Calculate total students under this faculty
    student_ids = set()
    for sub in subjects:
        student_list = StudentProfile.objects.filter(course=sub.course, semester=sub.semester)
        for stud in student_list:
            student_ids.add(stud.id)
    total_students_reached = len(student_ids)

    # Calculate pending evaluations
    pending_submissions = AssignmentSubmission.objects.filter(
        assignment__created_by=profile, 
        is_evaluated=False
    ).order_by('-submitted_at')
    
    context = {
        'profile': profile,
        'subjects': subjects,
        'subjects_count': subjects_count,
        'quizzes': quizzes,
        'quizzes_count': quizzes_count,
        'assignments': assignments,
        'assignments_count': assignments_count,
        'total_students_reached': total_students_reached,
        'pending_submissions': pending_submissions,
    }
    return render(request, 'dashboard/faculty_dashboard.html', context)

@login_required
def grade_submission(request, submission_id):
    if request.user.role != 'FACULTY':
        messages.error(request, "Unauthorized action.")
        return redirect('home')
        
    faculty_profile = request.user.faculty_profile
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, assignment__created_by=faculty_profile)
    
    if request.method == 'POST':
        marks = request.POST.get('marks')
        feedback = request.POST.get('feedback')
        
        try:
            submission.marks_obtained = float(marks)
            submission.feedback = feedback
            submission.is_evaluated = True
            submission.save()
            messages.success(request, f"Successfully graded submission for student ID {submission.student.student_id}.")
        except ValueError:
            messages.error(request, "Invalid marks value entered.")
        except Exception as e:
            messages.error(request, f"Error saving grade: {str(e)}")
            
    return redirect('faculty_dashboard')

@login_required
def add_assignment(request):
    if request.user.role != 'FACULTY':
        messages.error(request, "Unauthorized action.")
        return redirect('home')
        
    try:
        faculty_profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('home')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        subject_id = request.POST.get('subject')
        deadline_str = request.POST.get('deadline')
        max_marks = request.POST.get('max_marks', 100)
        file = request.FILES.get('file')
        
        try:
            subject = get_object_or_404(Subject, id=subject_id, faculty=faculty_profile)
            deadline = timezone.make_aware(datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M"))
            
            Assignment.objects.create(
                title=title,
                description=description,
                subject=subject,
                created_by=faculty_profile,
                deadline=deadline,
                max_marks=int(max_marks),
                file=file
            )
            messages.success(request, f"Assignment '{title}' has been successfully created.")
        except Exception as e:
            messages.error(request, f"Error creating assignment: {str(e)}")
            
    return redirect('faculty_dashboard')

@login_required
def add_quiz(request):
    if request.user.role != 'FACULTY':
        messages.error(request, "Unauthorized action.")
        return redirect('home')
        
    try:
        faculty_profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('home')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        subject_id = request.POST.get('subject')
        duration_minutes = request.POST.get('duration_minutes', 30)
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        
        try:
            subject = get_object_or_404(Subject, id=subject_id, faculty=faculty_profile)
            start_time = timezone.make_aware(datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M"))
            end_time = timezone.make_aware(datetime.strptime(end_time_str, "%Y-%m-%dT%H:%M"))
            
            Quiz.objects.create(
                title=title,
                description=description,
                subject=subject,
                created_by=faculty_profile,
                duration_minutes=int(duration_minutes),
                start_time=start_time,
                end_time=end_time,
                is_active=True
            )
            messages.success(request, f"Quiz '{title}' has been successfully created.")
        except Exception as e:
            messages.error(request, f"Error creating quiz: {str(e)}")
            
    return redirect('faculty_dashboard')

@login_required
def add_question(request, quiz_id):
    if request.user.role != 'FACULTY':
        messages.error(request, "Unauthorized action.")
        return redirect('home')
        
    try:
        faculty_profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('home')
        
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=faculty_profile)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        option_a = request.POST.get('option_a')
        option_b = request.POST.get('option_b')
        option_c = request.POST.get('option_c')
        option_d = request.POST.get('option_d')
        correct_option = request.POST.get('correct_option')
        marks = request.POST.get('marks', 1)
        
        try:
            Question.objects.create(
                quiz=quiz,
                text=text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option,
                marks=int(marks)
            )
            messages.success(request, f"Question added successfully to Quiz '{quiz.title}'.")
        except Exception as e:
            messages.error(request, f"Error adding question: {str(e)}")
            
    return redirect('faculty_dashboard')

# ----------------- CLASS SCHEDULING -----------------
@login_required
def faculty_schedule(request):
    if request.user.role != 'FACULTY':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('home')
        
    subjects = Subject.objects.filter(faculty=profile)
    slots = TimetableSlot.objects.filter(subject__in=subjects).order_by('day_of_week', 'start_time')
    
    context = {
        'slots': slots,
    }
    return render(request, 'dashboard/faculty_schedule.html', context)


# ----------------- MARKS & RESULTS -----------------
@login_required
def faculty_marks(request):
    if request.user.role != 'FACULTY':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('home')
        
    subjects = Subject.objects.filter(faculty=profile).order_by('code')
    exams = ExamSchedule.objects.filter(subject__in=subjects).order_by('-date')
    
    # Selected filters
    exam_id = request.GET.get('exam')
    student_results = []
    selected_exam = None
    
    if exam_id:
        selected_exam = get_object_or_404(ExamSchedule, id=exam_id, subject__in=subjects)
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
    return render(request, 'dashboard/faculty_marks.html', context)

@login_required
def add_exam(request):
    if request.user.role != 'FACULTY':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('home')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        subject_id = request.POST.get('subject')
        exam_type = request.POST.get('exam_type')
        date_str = request.POST.get('date')
        max_marks = request.POST.get('max_marks', 100)
        
        try:
            # Secure subject access check
            subject = get_object_or_404(Subject, id=subject_id, faculty=profile)
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
            
    return redirect('faculty_marks')

@login_required
def save_marks(request):
    if request.user.role != 'FACULTY':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('home')
        
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        # Secure exam access check: must be taught by this faculty member
        exam = get_object_or_404(ExamSchedule, id=exam_id, subject__faculty=profile)
        
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
                    Result.objects.filter(exam_schedule=exam, student=stud).delete()
                    
            messages.success(request, "Student marks saved successfully.")
        except Exception as e:
            messages.error(request, f"Error saving marks: {str(e)}")
            
    return redirect(f'/dashboard/faculty/marks/?exam={exam_id}')

@login_required
def faculty_attendance(request):
    if request.user.role != 'FACULTY':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    try:
        profile = request.user.faculty_profile
    except FacultyProfile.DoesNotExist:
        messages.error(request, "Faculty profile not found.")
        return redirect('home')
        
    subjects = Subject.objects.filter(faculty=profile).order_by('code')
    
    # Selected filters
    subject_id = request.GET.get('subject')
    student_id = request.GET.get('student')
    
    # Date variables
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    month_name = calendar.month_name[month]
    months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years_list = range(today.year - 2, today.year + 3)
    
    students = StudentProfile.objects.none()
    cal_grid = []
    selected_subject = None
    selected_student = None
    
    if subject_id:
        selected_subject = get_object_or_404(Subject, id=subject_id, faculty=profile)
        # Find students enrolled in the course and semester of the subject
        students = StudentProfile.objects.filter(
            course=selected_subject.course, 
            semester=selected_subject.semester
        ).order_by('student_id')
        
        if student_id:
            selected_student = get_object_or_404(StudentProfile, id=student_id, course=selected_subject.course, semester=selected_subject.semester)
            
            # Get existing attendance records for the month
            records = AttendanceRecord.objects.filter(
                student=selected_student,
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
        'students': students,
        'selected_subject_id': int(subject_id) if subject_id else None,
        'selected_student_id': int(student_id) if student_id else None,
        'selected_subject': selected_subject,
        'selected_student': selected_student,
        'selected_month': month,
        'selected_year': year,
        'month_name': month_name,
        'months_list': months_list,
        'years_list': years_list,
        'cal_grid': cal_grid,
    }
    return render(request, 'dashboard/faculty_attendance.html', context)
