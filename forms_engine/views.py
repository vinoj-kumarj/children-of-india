from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from forms_engine.models import FormVersion
from submissions.models import Submission, SubmissionFieldValue
from workflow.services import WorkflowService


# ===============================
# List Forms View
# ===============================
@login_required
def list_forms(request):
    forms = FormVersion.objects.filter(is_published=True).order_by("-version_number")
    return render(request, "forms_engine/list_forms.html", {"forms": forms})


# ===============================
# Submit Draft → Move to Submitted
# ===============================
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

    # Perform workflow transition (records audit as well)
    WorkflowService.transition(submission, request.user, "submit")

    return redirect("dashboard")


# ===============================
# Fill Form View
# ===============================
@login_required
def fill_form(request, version_id):
    form_version = get_object_or_404(
        FormVersion,
        id=version_id,
        is_published=True
    )

    # Handle legacy schema wrapping
    full_schema = form_version.schema_json or {}

    if isinstance(full_schema, dict) and "schema_json" in full_schema:
        schema = full_schema.get("schema_json", {})
    else:
        schema = full_schema if isinstance(full_schema, dict) else {}

    raw_fields = schema.get("fields", [])

    # Normalize fields
    fields = []
    for f in raw_fields:
        name = f.get("name") or f.get("field_key")
        ftype = f.get("type") or f.get("field_type")
        label = f.get("label") or f.get("label_json") or {"en": name or ""}

        if not name:
            continue

        fields.append({
            "name": name,
            "type": ftype,
            "label": label,
            "options": f.get("options", [])
        })

    # ===============================
    # Handle Form Submit (Save Draft)
    # ===============================
    if request.method == "POST":

        submission = Submission.objects.create(
            form_version=form_version,
            user=request.user,
            workflow_state="draft"
        )

        for field in fields:
            field_key = field["name"]

            # Handle file upload separately
            if field["type"] == "file":
                file_obj = request.FILES.get(field_key)

                SubmissionFieldValue.objects.create(
                    submission=submission,
                    field_key=field_key,
                    file=file_obj
                )
            else:
                value = request.POST.getlist(field_key)

                if len(value) == 1:
                    value = value[0]
                elif len(value) == 0:
                    value = None

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