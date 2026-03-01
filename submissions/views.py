from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Submission


@login_required
def submit_submission(request, submission_id):
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        user=request.user
    )

    if submission.workflow_state != "draft":
        return redirect("dashboard")

    submission.workflow_state = "submitted"
    submission.submitted_at = timezone.now()
    submission.save()

    return redirect("dashboard")