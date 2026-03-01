from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from submissions.models import Submission
from .models import SubmissionReview, WorkflowComment, WorkflowAudit


def is_coordinator(user):
    return user.role == "coordinator"

def is_lead(user):
    return user.role == "lead"

def is_field_coordinator(user):
    return user.role == "field"


@login_required
def coordinator_dashboard(request):
    if not is_coordinator(request.user):
        return redirect("dashboard")

    submissions = Submission.objects.filter(workflow_state="submitted")

    return render(request, "workflow/coordinator_dashboard.html", {
        "submissions": submissions
    })


@login_required
def coordinator_review(request, submission_id):
    if not is_coordinator(request.user):
        return redirect("dashboard")

    submission = get_object_or_404(Submission, id=submission_id)
    reviews = submission.reviews.all().order_by("-reviewed_at")
    comments = submission.comments.all().order_by("-created_at")
    audits = submission.audits.all().order_by("-created_at")

    if request.method == "POST":
        comment = request.POST.get("comment")

        old_state = submission.workflow_state
        submission.workflow_state = "lead_review"
        submission.save()

        SubmissionReview.objects.create(
            submission=submission,
            reviewer=request.user,
            from_state=old_state,
            to_state="lead_review",
            comment=comment
        )

        WorkflowAudit.objects.create(
            submission=submission,
            user=request.user,
            from_state=old_state,
            to_state="lead_review",
            action="send_to_lead"
        )

        return redirect("coordinator_dashboard")

    return render(request, "workflow/coordinator_review.html", {
        "submission": submission,
        "reviews": reviews,
        "comments": comments,
        "audits": audits
    })


def is_lead(user):
    return user.role == "lead"


@login_required
def lead_dashboard(request):
    if not is_lead(request.user):
        return redirect("dashboard")

    submissions = Submission.objects.filter(workflow_state="lead_review")

    return render(request, "workflow/lead_dashboard.html", {
        "submissions": submissions
    })


@login_required
def lead_review(request, submission_id):
    if not is_lead(request.user):
        return redirect("dashboard")

    submission = get_object_or_404(Submission, id=submission_id)
    reviews = submission.reviews.all().order_by("-reviewed_at")
    comments = submission.comments.all().order_by("-created_at")
    audits = submission.audits.all().order_by("-created_at")

    if request.method == "POST":
        action = request.POST.get("action")
        comment = request.POST.get("comment")

        old_state = submission.workflow_state

        if action == "approve":
            submission.workflow_state = "approved"
        elif action == "reject":
            submission.workflow_state = "rejected"

        submission.save()

        SubmissionReview.objects.create(
            submission=submission,
            reviewer=request.user,
            from_state=old_state,
            to_state=submission.workflow_state,
            comment=comment
        )

        WorkflowAudit.objects.create(
            submission=submission,
            user=request.user,
            from_state=old_state,
            to_state=submission.workflow_state,
            action=action
        )

        return redirect("lead_dashboard")

    return render(request, "workflow/lead_review.html", {
        "submission": submission,
        "reviews": reviews,
        "comments": comments,
        "audits": audits,
        "reviews": reviews,
        "comments": comments,
        "audits": audits
    })


@login_required
def field_coordinator_submissions(request):
    """Field coordinator view to see their submission history with comments and status."""
    if not is_field_coordinator(request.user):
        return redirect("dashboard")

    submissions = Submission.objects.filter(user=request.user).order_by("-created_at")

    context = {
        "submissions": submissions,
        "user_role": "field"
    }
    return render(request, "workflow/field_submissions_history.html", context)


@login_required
def field_coordinator_submission_detail(request, submission_id):
    """Field coordinator view to see a single submission with all comments and feedback."""
    if not is_field_coordinator(request.user):
        return redirect("dashboard")

    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    reviews = submission.reviews.all().order_by("-reviewed_at")
    audits = submission.audits.all().order_by("-created_at")

    context = {
        "submission": submission,
        "reviews": reviews,
        "audits": audits
    }
    return render(request, "workflow/field_submission_detail.html", context)