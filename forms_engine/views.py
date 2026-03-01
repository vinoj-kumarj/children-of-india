
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from forms_engine.models import FormVersion
from submissions.models import Submission, SubmissionFieldValue


@login_required
def submit_submission(request, submission_id):
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        user=request.user
    )

    # Only allow draft to be submitted
    if submission.workflow_state != "draft":
        return redirect("dashboard")

    submission.workflow_state = "submitted"
    submission.submitted_at = timezone.now()
    submission.save()

    return redirect("dashboard")

@login_required
def list_forms(request):
    forms = FormVersion.objects.all()
    #forms = FormVersion.objects.filter(is_published=True)

    print("FORMS:", forms)

    return render(request, "forms_engine/list_forms.html", {
        "forms": forms
    })

@login_required
def fill_form(request, version_id):
    form_version = get_object_or_404(
        FormVersion,
        id=version_id,
        is_published=True
    )

    full_schema = form_version.schema_json
    schema = full_schema.get("schema_json", {})
    fields = schema.get("fields", [])

    if request.method == "POST":

        # 1️⃣ Create Submission
        submission = Submission.objects.create(
            form_version=form_version,
            user=request.user,
            workflow_state="draft"
        )

        # 2️⃣ Save each field separately
        for field in fields:
            field_key = field["name"]
            value = request.POST.get(field_key)

            SubmissionFieldValue.objects.create(
                submission=submission,
                field_key=field_key,
                value_json=value
            )

        return redirect("dashboard")

    return render(request, "forms_engine/fill_form.html", {
        "form_version": form_version,
        "fields": fields,
        "title": schema.get("title", "Dynamic Form")
    })