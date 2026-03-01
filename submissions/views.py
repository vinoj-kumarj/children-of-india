from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Submission
from workflow.services import WorkflowService


@login_required
def submit_submission(request, submission_id):
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        user=request.user
    )

    if submission.workflow_state != "draft":
        return redirect("dashboard")

    # use workflow service to transition state and log audit
    WorkflowService.transition(submission, request.user, "submit")

    return redirect("dashboard")