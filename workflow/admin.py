from django.contrib import admin
from .models import WorkflowComment, WorkflowAudit


@admin.register(WorkflowComment)
class WorkflowCommentAdmin(admin.ModelAdmin):
    list_display = ("submission", "user", "action_type", "created_at")


@admin.register(WorkflowAudit)
class WorkflowAuditAdmin(admin.ModelAdmin):
    list_display = ("submission", "from_state", "to_state", "created_at")