import uuid
from django.db import models
from django.conf import settings
from submissions.models import Submission



class SubmissionReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    from_state = models.CharField(max_length=50)
    to_state = models.CharField(max_length=50)

    comment = models.TextField(blank=True, null=True)

    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.submission} - {self.to_state}"


class WorkflowComment(models.Model):
    ACTION_CHOICES = (
        ("submit", "Submit"),
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("send_back", "Send Back"),
        ("comment", "Comment"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    action_type = models.CharField(max_length=50, choices=ACTION_CHOICES)
    comment_text = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action_type} by {self.user.email}"


class WorkflowAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="audits")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    from_state = models.CharField(max_length=50)
    to_state = models.CharField(max_length=50)

    action = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_state} → {self.to_state}"