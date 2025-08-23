from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import User, LogEntry, Comment
from .forms import LogEntryForm, CommentForm

def home(request):
    """
    A simple home page that redirects authenticated users to their dashboard
    and shows a landing page for unauthenticated users.
    """
    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role in ['academic_supervisor', 'industry_supervisor']:
            return redirect('supervisor_dashboard')
    
    return render(request, 'logbook/home.html')

# Custom decorator to restrict access to students only
def student_required(view_func):
    def _wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'student':
            return redirect('login') # Or a more appropriate page
        return view_func(request, *args, **kwargs)
    return _wrapper

# Custom decorator for supervisors
def supervisor_required(view_func):
    def _wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ['academic_supervisor', 'industry_supervisor']:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapper

# -----------------------------
# Student-Specific Views
# -----------------------------
@login_required
@student_required
def student_dashboard(request):
    # This view now only shows logs for the logged-in student
    logs = LogEntry.objects.filter(student=request.user).order_by('-date')
    return render(request, 'logbook/student_dashboard.html', {'logs': logs})

@login_required
@student_required
def logentry_create(request):
    if request.method == "POST":
        form = LogEntryForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            # Assign the log entry to the currently logged-in student
            log.student = request.user
            log.save()
            return redirect('student_dashboard')
    else:
        form = LogEntryForm()
    return render(request, 'logbook/logentry_form.html', {'form': form})

# -----------------------------
# Supervisor-Specific Views
# -----------------------------
@login_required
@supervisor_required
def supervisor_dashboard(request):
    # Fetch logs for students assigned to this supervisor
    assigned_students = request.user.academic_profile.students.all() # Assuming the user is an academic supervisor
    # Or, if they are an industry supervisor:
    # assigned_students = request.user.industry_profile.interns.all()
    
    # Fetch all log entries for these assigned students
    logs = LogEntry.objects.filter(student__in=[s.user for s in assigned_students]).order_by('-date')
    return render(request, 'logbook/supervisor_dashboard.html', {'students': assigned_students, 'logs': logs})

@login_required
@supervisor_required
def log_detail(request, log_id):
    log = get_object_or_404(LogEntry, id=log_id)
    # Check if the supervisor is authorized to view this log
    if not (request.user == log.student.student_profile.academic_supervisor.user or request.user == log.student.student_profile.industry_supervisor.user):
        return redirect('supervisor_dashboard') # Or an unauthorized page
        
    comments = Comment.objects.filter(log_entry=log).order_by('created_at')
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.log_entry = log
            comment.author = request.user
            comment.save()
            return redirect('log_detail', log_id=log.id)
    else:
        form = CommentForm()

    return render(request, 'logbook/log_detail.html', {'log': log, 'comments': comments, 'form': form})