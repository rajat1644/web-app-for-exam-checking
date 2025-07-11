from django.urls import path
from . import views
from .views import role_based_redirect_view

urlpatterns = [
    path('redirect-after-login/', role_based_redirect_view, name='role_redirect'),
    path('', views.task_list, name='task_list'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('history/', views.submission_history, name='submission_history'),
    path('review-dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('review/<int:submission_id>/', views.review_detail, name='review_detail'),
    path('submitted-dashboard/', views.submitted_dashboard, name='submitted_dashboard'),
    path('completed/', views.completed_tasks, name='completed_tasks'),
    path('', views.role_based_redirect_view, name='home'),
    path('submission/<int:submission_id>/view/', views.view_submission, name='view_submission'),
    path('edit-submission/<int:submission_id>/', views.edit_submission, name='edit_submission'),
    path('save-edited-submission/<int:submission_id>/', views.save_edited_submission, name='save_edited_submission'),

]
