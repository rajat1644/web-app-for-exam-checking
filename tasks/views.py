# ✅ FINAL WORKING `views.py` with all previously missing functions restored

import os
import base64
import uuid
import json
import re
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Task, Submission, TaskImage, QuestionPaper
from .json import analyze_multiple_canvas_jsons
from .utils import validate_submission

# ✅ Redirect after login
@login_required
def role_based_redirect_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/')
    else:
        return redirect('/dashboard/')

# ✅ User profile form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

# ✅ Profile view
@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'registration/profile.html', {'form': form})

# ✅ Register view

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# ✅ Task list
@login_required
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user, is_completed=False)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, assigned_to=request.user)
    images = TaskImage.objects.filter(task=task)
    questions = task.question_paper.questions if task.question_paper else []

    if request.method == 'POST':
        canvas_payload = request.POST.get("all_canvas_data")
        if not canvas_payload:
            messages.error(request, "Submission is empty.")
            return redirect('task_detail', task_id=task_id)

        try:
            canvas_items = json.loads(canvas_payload)
        except json.JSONDecodeError:
            messages.error(request, "Failed to parse annotation data.")
            return redirect('task_detail', task_id=task_id)

        image_files, canvas_jsons = [], []
        question_marks = {}

        for item in canvas_items:
            image_data = item.get("image_data")
            canvas_data = item.get("canvas_data")
            if image_data and canvas_data and canvas_data.strip() not in ["[]", "null", ""]:
                try:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    file_name = f"{uuid.uuid4()}.{ext}"
                    image_file = ContentFile(base64.b64decode(imgstr), name=file_name)
                    image_files.append(image_file)
                    canvas_jsons.append(canvas_data)

                    json_obj = json.loads(canvas_data)
                    for obj in json_obj.get("objects", []):
                        qid = str(obj.get("question_id"))
                        mark = float(obj.get("marks", 0))
                        if qid:
                            question_marks[qid] = question_marks.get(qid, 0) + mark
                except Exception:
                    continue

        if len(image_files) != images.count():
            messages.error(request, "Please annotate all task images before submitting.")
            return redirect('task_detail', task_id=task_id)

        submission = Submission.objects.create(
            user=request.user,
            task=task,
            edited_image=image_files[0],
            canvas_json=json.dumps(canvas_jsons),
            marks_per_question=question_marks,
            total_marks=sum(question_marks.values()) if question_marks else 0,
        )

        validate_submission(submission, task.question_paper)

        if not submission.marks_per_question:
            submission.status = "Rejected"
        elif submission.warnings:
            submission.status = "Pending"
        else:
            submission.status = "Approved"
            task.is_completed = True
            task.save()

        submission.save()
        return render(request, 'submit_success.html', {
            'submission': submission,
            'questions': questions
        })

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'images': images,
        'questions': questions
    })

# ✅ View past submissions
@login_required
def submission_history(request):
    submissions = request.user.submission_set.select_related('task').all()
    return render(request, 'tasks/submission_history.html', {'submissions': submissions})

# ✅ Completed tasks view
@login_required
def completed_tasks(request):
    completed = Task.objects.filter(assigned_to=request.user, is_completed=True)
    task_data = []

    for task in completed:
        submission = Submission.objects.filter(user=request.user, task=task).order_by('-submitted_at').first()
        task_data.append({
            'task': task,
            'submission': submission
        })

    return render(request, 'tasks/completed_tasks.html', {'task_data': task_data})


# ✅ User dashboard
@login_required
def dashboard(request):
    user = request.user
    assigned_tasks = Task.objects.filter(assigned_to=user)
    return render(request, 'dashboard/dashboard.html', {
        'total_tasks': assigned_tasks.count(),
        'completed_tasks': assigned_tasks.filter(is_completed=True).count(),
        'pending_tasks': assigned_tasks.filter(is_completed=False).count(),
    })

# ✅ Agent dashboard to review submissions
@staff_member_required
def agent_dashboard(request):
    submissions = Submission.objects.filter(status__in=['Pending', 'Rejected'])
    return render(request, 'agent_dashboard.html', {'submissions': submissions})

# ✅ Review details page
@staff_member_required
def review_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        submission.comments = request.POST.get('comments', '')
        if request.POST.get('action') == 'approve':
            submission.status = 'Approved'
        elif request.POST.get('action') == 'reject':
            submission.status = 'Rejected'
        submission.save()
        return redirect('agent_dashboard')
    return render(request, 'review_detail.html', {'submission': submission})

# ✅ View only approved submissions
@staff_member_required
def submitted_dashboard(request):
    submissions = Submission.objects.filter(status='Approved')
    return render(request, 'submitted_dashboard.html', {'submissions': submissions})

@login_required
def view_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)

    # Parse canvas JSON
    try:
        canvas_data_list = json.loads(submission.canvas_json or "[]")
    except Exception:
        canvas_data_list = []

    image_annotations = []
    task_images = TaskImage.objects.filter(task=submission.task)
    for i, img in enumerate(task_images):
        if i < len(canvas_data_list):
            image_annotations.append({
                "image_url": img.image.url,
                "canvas_data": canvas_data_list[i]
            })

    # Extract question data
    questions = submission.task.question_paper.questions if submission.task.question_paper else []

    return render(request, 'tasks/view_submission.html', {
    'submission': submission,
    'annotation_data': json.dumps(image_annotations),
    'image_annotations': image_annotations,
    'questions': questions,
})

 
@login_required
@csrf_exempt
def edit_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    task = submission.task
    questions = task.question_paper.questions if task.question_paper else []

    if request.method == 'POST':
        canvas_payload = request.POST.get("all_canvas_data")
        if not canvas_payload:
            messages.error(request, "Submission is empty.")
            return redirect('edit_submission', submission_id=submission_id)

        try:
            canvas_items = json.loads(canvas_payload)
        except json.JSONDecodeError:
            messages.error(request, "Failed to parse annotation data.")
            return redirect('edit_submission', submission_id=submission_id)

        image_files, canvas_jsons = [], []
        question_marks = {}

        for item in canvas_items:
            image_data = item.get("image_data")
            canvas_data = item.get("canvas_data")
            if image_data and canvas_data and canvas_data.strip() not in ["[]", "null", ""]:
                try:
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    file_name = f"{uuid.uuid4()}.{ext}"
                    image_file = ContentFile(base64.b64decode(imgstr), name=file_name)
                    image_files.append(image_file)
                    canvas_jsons.append(canvas_data)

                    json_obj = json.loads(canvas_data)
                    for obj in json_obj.get("objects", []):
                        qid = str(obj.get("question_id"))
                        mark = float(obj.get("marks", 0))
                        if qid:
                            question_marks[qid] = question_marks.get(qid, 0) + mark
                except Exception:
                    continue

        if len(image_files) != TaskImage.objects.filter(task=task).count():
            messages.error(request, "Please annotate all task images before saving.")
            return redirect('edit_submission', submission_id=submission_id)

        submission.edited_image = image_files[0] if image_files else submission.edited_image
        submission.canvas_json = json.dumps(canvas_jsons)
        submission.marks_per_question = question_marks
        submission.total_marks = sum(question_marks.values()) if question_marks else 0

        validate_submission(submission, task.question_paper)

        if not submission.marks_per_question:
            submission.status = "Rejected"
        elif submission.warnings:
            submission.status = "Pending"
        else:
            submission.status = "Approved"
            task.is_completed = True
            task.save()

        submission.save()
        return render(request, 'submit_success.html', {
            'submission': submission,
            'questions': questions
        })

    annotation_data = json.loads(submission.canvas_json or "[]")
    task_images = TaskImage.objects.filter(task=task)

    image_annotations = []
    for i, img in enumerate(task_images):
        canvas_data = annotation_data[i] if i < len(annotation_data) else {}
        image_annotations.append({
            "image_url": img.image.url,
            "canvas_data": canvas_data
        })

    return render(request, 'edit_submission.html', {
        'submission': submission,
        'questions': questions,
        'image_annotations': image_annotations,
        'annotation_data': json.dumps(image_annotations),
    })


@csrf_exempt
@login_required
def save_edited_submission(request, submission_id):
    if request.method == 'POST':
        submission = get_object_or_404(Submission, id=submission_id, user=request.user)
        data = json.loads(request.body)
        submission.canvas_json = data.get('canvas_json', '')
        submission.marks_json = data.get('marks_json', '{}')
        submission.save()
        return JsonResponse({'status': 'success'})