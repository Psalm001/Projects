
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # General URLs
    path('', views.home, name='home'),  # A homepage to direct users
    path('login/', auth_views.LoginView.as_view(template_name='logbook/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Student URLs
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('log/add/', views.logentry_create, name='logentry_create'),

    # Supervisor URLs
    path('supervisor/dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('log/<int:log_id>/', views.log_detail, name='log_detail'),
]