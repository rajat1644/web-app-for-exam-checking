from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def public_demo(request):
    return HttpResponse("""
    <html>
      <head><title>Exam Checker</title></head>
      <body style='font-family:sans-serif;padding:2rem;'>
        <h1>📝 Web-based Exam Checking App</h1>
        <p>This is a <strong>live preview</strong> of the frontend.</p>
        <p>Database features (login, marking, admin) are disabled in this version.</p>
      </body>
    </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', public_demo),  # 👈 Make this the default page
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('internal/', include('tasks.urls')),
    path('', include('tasks.urls')),

    path('accounts/', include('django.contrib.auth.urls')),

    # Password reset flow
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # ✅ Password change for logged-in users
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html'), name='password_change'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'), name='password_change_done'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
