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

from .models import Task, Submission, TaskImage, QuestionPaper
from .json import analyze_multiple_canvas_jsons

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

# ✅ Register view (was previously removed)
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

# ✅ Task detail with annotation + submission logic
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
        warnings = []

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
            status="Submitted"
        )

        max_marks_map = {str(q['id']): q['max_marks'] for q in questions}
        optional_groups = {}
        for q in questions:
            group = q.get("optional_group")
            if group:
                optional_groups.setdefault(group, []).append(str(q['id']))

        for qid, mark in question_marks.items():
            max_mark = max_marks_map.get(qid)
            if max_mark and mark > max_mark:
                warnings.append(f"Q{qid} given {mark}, max is {max_mark}")

        for group, qids in optional_groups.items():
            attempted = [qid for qid in qids if qid in question_marks and question_marks[qid] > 0]
            if len(attempted) > 2:
                warnings.append(f"Optional Group {group} over-attempted: {attempted}")

        total = sum(question_marks.values())
        submission.result = f"Total Marks: {total}"
        submission.marks_per_question = question_marks
        submission.total_marks = total
        submission.warnings = warnings

        def extract_score(result):
            if isinstance(result, (int, float)):
                return float(result)
            try:
                match = re.search(r"Total Marks:\s*([0-9]*\.?[0-9]+)", str(result))
                if match:
                    return float(match.group(1))
            except:
                pass
            return None

        score = extract_score(submission.result)
        if score is not None:
            submission.score = score
            if score >= 10:
                submission.status = "Approved"
                task.is_completed = True
                task.save()
            else:
                submission.status = "Pending"
        else:
            submission.status = "Rejected"

        submission.save()
        return render(request, 'submit_success.html', {'submission': submission, 'questions': questions})

    return render(request, 'tasks/task_detail.html', {'task': task, 'images': images, 'questions': questions})

# ✅ View past submissions
@login_required
def submission_history(request):
    submissions = request.user.submission_set.select_related('task').all()
    return render(request, 'tasks/submission_history.html', {'submissions': submissions})

# ✅ Completed tasks view
@login_required
def completed_tasks(request):
    completed = Task.objects.filter(assigned_to=request.user, is_completed=True)
    return render(request, 'tasks/completed_tasks.html', {'completed_tasks': completed})

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
        if submission.result and not submission.score:
            submission.score = submission.result
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
