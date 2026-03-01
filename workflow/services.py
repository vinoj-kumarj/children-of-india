from django.utils import timezone
from submissions.models import Submission
from .models import WorkflowComment, WorkflowAudit


class WorkflowService:

    @staticmethod
    def transition(submission, user, action, comment_text=None):

        current_state = submission.workflow_state

        # ---- STATE MACHINE RULES ----
        transitions = {
            "draft": {
                "submit": "coordinator_review",
            },
            "coordinator_review": {
                "approve": "lead_review",
                "reject": "rejected",
                "send_back": "resubmission",
            },
            "lead_review": {
                "approve": "approved",
                "reject": "rejected",
                "send_back": "resubmission",
            },
            "resubmission": {
                "submit": "coordinator_review",
            }
        }

        if current_state not in transitions:
            raise Exception("Invalid current state")

        if action not in transitions[current_state]:
            raise Exception("Invalid transition")

        new_state = transitions[current_state][action]

        # Update submission state
        submission.workflow_state = new_state

        if action == "submit":
            submission.submitted_at = timezone.now()

        submission.save()

        # Save comment
        WorkflowComment.objects.create(
            submission=submission,
            user=user,
            action_type=action,
            comment_text=comment_text,
        )

        # Save audit
        WorkflowAudit.objects.create(
            submission=submission,
            user=user,
            from_state=current_state,
            to_state=new_state,
            action=action,
        )

        return submission