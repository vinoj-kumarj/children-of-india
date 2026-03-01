from django.contrib import admin
from .models import Submission, SubmissionFieldValue


class SubmissionFieldInline(admin.TabularInline):
    model = SubmissionFieldValue
    extra = 0


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "form_version", "user", "workflow_state", "created_at")
    inlines = [SubmissionFieldInline]