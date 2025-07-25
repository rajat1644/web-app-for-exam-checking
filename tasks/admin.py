from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.shortcuts import redirect, render
from django.urls import reverse, path
from django.http import HttpResponseRedirect
from django.forms import formset_factory
import json

from .models import (
    Task, TaskImage, Submission, StaffUser,
    ReviewSubmissions, SubmittedSubmissions, QuestionPaper, QuestionInlineForm
)

QuestionInlineFormSet = formset_factory(QuestionInlineForm, extra=3)

class QuestionPaperAdmin(admin.ModelAdmin):
    change_form_template = 'admin/custom_question_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/change/', self.admin_site.admin_view(self.change_view_custom), name='tasks_questionpaper_change'),
            path('add/', self.admin_site.admin_view(self.add_view_custom), name='tasks_questionpaper_add'),
        ]
        return custom_urls + urls

    def add_view_custom(self, request):
        if request.method == 'POST':
            title = request.POST.get("title", "")
            formset = QuestionInlineFormSet(request.POST)
            if formset.is_valid():
                questions = []
                for form in formset:
                    if form.cleaned_data.get('text'):
                        questions.append({
                            "id": form.cleaned_data['qid'],
                            "text": form.cleaned_data['text'],
                            "max_marks": form.cleaned_data['max_marks'],
                            "optional_group": form.cleaned_data['optional_group']
                        })
                instance = QuestionPaper.objects.create(title=title, questions=questions)
                return redirect(f'/admin/tasks/questionpaper/{instance.pk}/change/')
        else:
            formset = QuestionInlineFormSet(initial=[{} for _ in range(3)])

        context = {
            'opts': self.model._meta,
            'formset': formset,
            'title': 'Add QuestionPaper',
            'original': None,
        }
        return render(request, 'admin/custom_question_form.html', context)

    def change_view_custom(self, request, object_id):
        instance = QuestionPaper.objects.get(pk=object_id)
        if request.method == 'POST':
            title = request.POST.get("title", "")
            formset = QuestionInlineFormSet(request.POST)
            if formset.is_valid():
                questions = []
                for form in formset:
                    if form.cleaned_data.get('text'):
                        questions.append({
                            "id": form.cleaned_data['qid'],
                            "text": form.cleaned_data['text'],
                            "max_marks": form.cleaned_data['max_marks'],
                            "optional_group": form.cleaned_data['optional_group']
                        })
                instance.title = title
                instance.questions = questions
                instance.save()
                return redirect(f'/admin/tasks/questionpaper/{object_id}/change/')
        else:
            initial_data = []
            if instance.questions:
                for q in instance.questions:
                    initial_data.append({
                        'qid': q.get("id", ""),
                        'text': q.get("text", ""),
                        'max_marks': q.get("max_marks", ""),
                        'optional_group': q.get("optional_group", "")
                    })
            if not initial_data:
                initial_data = [{} for _ in range(3)]
            formset = QuestionInlineFormSet(initial=initial_data)

        context = {
            'opts': self.model._meta,
            'original': instance,
            'formset': formset,
            'title': f'Edit QuestionPaper: {instance.title}',
            'title_value': instance.title
        }
        return render(request, 'admin/custom_question_form.html', context)

admin.site.register(QuestionPaper, QuestionPaperAdmin)

class SubmittedSubmissionsAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect(reverse('submitted_dashboard'))

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request): return False

admin.site.register(SubmittedSubmissions, SubmittedSubmissionsAdmin)

class TaskImageInline(admin.TabularInline):
    model = TaskImage
    extra = 1
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            print("IMAGE URL:", obj.image.url)  # debug print
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return ""

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'is_completed']
    inlines = [TaskImageInline]

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'submitted_at', 'result', 'status']
    readonly_fields = ['submitted_at']
    list_filter = ['status', 'submitted_at']

@admin.register(ReviewSubmissions)
class ReviewSubmissionsAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('agent_dashboard'))

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request): return False

@admin.register(StaffUser)
class StaffUserAdmin(BaseUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=True)

admin.site.unregister(User)
admin.site.register(User, BaseUserAdmin)
