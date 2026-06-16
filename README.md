# Next-Generation College ERP System

An enterprise-grade, feature-rich, and secure **College ERP (Enterprise Resource Planning)** system built using **Python, Django, Django REST Framework, SQLite/PostgreSQL, and Bootstrap 5**. This platform includes separate login interfaces and specialized dashboards for **Admins, Faculty, and Students**.

---

## 🚀 Core Modules & Features

1. **Role-Based Dashboards & RBAC**:
   - Custom access control for Admins, Faculty, and Students.
   - Self-registration for students and faculty with a pending approval queue in the Admin dashboard.
2. **Learning Management System (LMS)**:
   - File uploads (PDFs, PPTs, DOCX, ZIPs), description editing, subject category tagging, and download counter tracking.
3. **Interactive MCQ Arena**:
   - Timed multiple-choice quizzes, randomize questions, slide-through question widgets, and automatic grading.
4. **Coding Practice Sandbox**:
   - Python code compiling terminal that executes students' submissions against test cases using secure subprocess runner, evaluating output matching, timeouts, and execution times.
5. **Assignment Workspace**:
   - Students upload assignments; faculty review details and submit grades/feedback inline.
6. **Attendance & Results**:
   - Instructors log daily presence. System computes percentages. Exam schedule tables and CGPA/transcript marksheet boards are updated instantly.
7. **REST APIs & JWT**:
   - Unified API router at `/api/` integrated with SimpleJWT token headers.

---

## 📂 Project Structure

```text
college_erp/
│
├── accounts/               # CustomUser registration, login, and RBAC permissions
│   ├── admin_auth/         # Admin login & register (verified via secret code)
│   ├── faculty_auth/       # Faculty self-registration & login
│   └── student_auth/       # Student self-registration & login
│
├── academics/              # Departments, Courses, Subjects, Semester, Timetable, Fees
├── students/               # Student Profile records
├── faculty/                # Faculty Profile records
├── dashboard/              # Sidebar template layouts & views (Admin, Faculty, Student UI)
├── lms/                    # Learning materials uploads & down-trackers
├── assignments/            # Homework schedules & grading
├── mcq_arena/              # Quiz builders & attempts
├── coding_practice/        # Python compiler test cases & code runner
├── attendance/             # Attendance marking logs
├── results/                # Marks entry transcripts
├── notifications/          # Notice board notifications
├── api/                    # Central REST serializers & viewset routing
│
├── templates/              # HTML layout shells
├── static/                 # Custom CSS / JS assets
└── media/                  # Uploaded materials & files
```

---

## 🛠️ Local Development Setup

### 1. Prerequisites
- Python 3.10+
- Pip

### 2. Installation
Clone the repository and move into the workspace directory, then execute the following steps:

1. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Create a `.env` file in the root folder (or copy `.env.example`):
   ```ini
   SECRET_KEY=django-insecure-prod-college-erp-system-key-2026
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_ENGINE=django.db.backends.sqlite3
   ```
4. **Apply Schema Migrations**:
   ```bash
   python manage.py migrate
   ```
5. **Seed Demo Data**:
   This seeds core departments, courses, subjects, quiz questions, coding problems, and creates three ready-to-test accounts:
   ```bash
   python seed.py
   ```
6. **Run Server**:
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🔑 Demo Account Credentials

Use these pre-populated credentials to log in and inspect the different portals:

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `adminpassword123` | Can approve new signups, manage departments, courses. |
| **Faculty** | `faculty` | `facultypassword123` | Can view schedule, mark attendance, edit quizzes, grade submissions. |
| **Student** | `student` | `studentpassword123` | Can upload assignments, solve coding practice, take quizzes. |

*Note: For registering additional Admins for review, the registration secret key is `ERPADMIN2026`.*

---

## 🐳 Docker Deployment Setup

Deploy the application stack (web service + PostgreSQL) with a single command:

```bash
docker-compose up --build
```
This boots a PostgreSQL database container and executes standard migrate rules.
