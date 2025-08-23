
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # This is the fix for the reverse accessor clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='logbook_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='logbook_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('academic_supervisor', 'Academic Supervisor'),
        ('industry_supervisor', 'Industry Supervisor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    matric_no = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username

# The Student and Supervisor models will now have a One-to-One relationship with the User model.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    course = models.CharField(max_length=100)
    academic_supervisor = models.ForeignKey('AcademicSupervisor', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    industry_supervisor = models.ForeignKey('IndustrySupervisor', on_delete=models.SET_NULL, null=True, blank=True, related_name='interns')

    def __str__(self):
        return f"{self.user.username} ({self.user.matric_no})"

class AcademicSupervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='academic_profile')
    designation = models.CharField(max_length=100)

    def __str__(self):
        return f"Academic Supervisor: {self.user.username}"

class IndustrySupervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='industry_profile')
    company = models.CharField(max_length=100)

    def __str__(self):
        return f"Industry Supervisor: {self.user.username}"

# The LogEntry and Comment models will link directly to the User model
class LogEntry(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")
    date = models.DateField()
    activity_description = models.TextField()

    def __str__(self):
        return f"{self.student.username} - {self.date}"

class Comment(models.Model):
    log_entry = models.ForeignKey(LogEntry, on_delete=models.CASCADE, related_name="comments")
    # This will now link to the user who made the comment
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.log_entry}"