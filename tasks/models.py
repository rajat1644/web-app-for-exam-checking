from django.db import models
from django.contrib.auth.models import User
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django import forms

# ✅ Admin Form for Question Entry
class QuestionInlineForm(forms.Form):
    qid = forms.IntegerField(label="ID", min_value=1, widget=forms.NumberInput(attrs={'class': 'vIntegerField'}))
    text = forms.CharField(label="Question Text", widget=forms.TextInput(attrs={'class': 'vTextField'}))
    max_marks = forms.FloatField(label="Max Marks", min_value=0, widget=forms.NumberInput(attrs={'class': 'vFloatField'}))
    optional_group = forms.CharField(label="Optional Group", required=False, widget=forms.TextInput(attrs={'class': 'vTextField'}))

# ✅ Question Paper with Embedded Questions JSON
class QuestionPaper(models.Model):
    title = models.CharField(max_length=255)
    questions = models.JSONField(default=list, blank=True)  # JSON field to hold questions

    def __str__(self):
        return self.title

# ✅ Core Task Model with QuestionPaper Link
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

# ✅ Images for Task Pages
class TaskImage(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tasks_image/extra/')

@receiver(post_delete, sender=TaskImage)
def delete_taskimage_file(sender, instance, **kwargs):
    if instance.image and instance.image.path and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

# ✅ Submission with JSON and Mark Tracking
class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    edited_image = models.ImageField(upload_to='edited/')
    canvas_json = models.TextField(blank=True, null=True)
    result = models.CharField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    comments = models.TextField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)

    # ✅ Mark Tracking
    marks_per_question = models.JSONField(null=True, blank=True)  # {"1": 4, "2": 5}
    total_marks = models.FloatField(null=True, blank=True)
    warnings = models.JSONField(null=True, blank=True)  # ["Q1 overmarked", "Too many optional answers"]

    def __str__(self):
        return f"{self.user.username}'s submission for {self.task.title}"

@receiver(post_delete, sender=Submission)
def delete_submission_file(sender, instance, **kwargs):
    if instance.edited_image and instance.edited_image.path and os.path.isfile(instance.edited_image.path):
        os.remove(instance.edited_image.path)

# ✅ Proxy: Staff Members for Admin Panel
class StaffUser(User):
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = 'Staff Member'
        verbose_name_plural = 'Staff Members'

# ✅ Proxy: Admin Dashboard for Review Submissions
class ReviewSubmissions(User):
    class Meta:
        proxy = True
        verbose_name = "🕵️ Review pending/rejected Submissions"
        verbose_name_plural = "🕵️ Review pending/rejected Submissions"

# ✅ Proxy: Final Submitted Approved Tasks
class SubmittedSubmissions(User):
    class Meta:
        proxy = True
        verbose_name = "📤 Submitted Dashboard"
        verbose_name_plural = "📤 Submitted Dashboard"
