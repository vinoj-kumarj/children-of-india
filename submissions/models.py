import uuid
from django.db import models
from django.conf import settings
from forms_engine.models import FormVersion


class Submission(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("coordinator_review", "Coordinator Review"),
        ("lead_review", "Lead Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("resubmission", "Resubmission Required"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    form_version = models.ForeignKey(FormVersion, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    workflow_state = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")

    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission {self.id}"


class SubmissionFieldValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="field_values")

    field_key = models.CharField(max_length=255)
    value_json = models.JSONField(blank=True, null=True)

    file = models.FileField(upload_to="submission_files/", blank=True, null=True)

    def __str__(self):
        return self.field_key