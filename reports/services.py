from django.db.models import Count
from django.utils import timezone
from submissions.models import Submission


class ReportService:

    @staticmethod
    def dashboard_summary(user):

        qs = Submission.objects.all()

        # Role-based filtering
        if user.role == "field":
            qs = qs.filter(user=user)

        if user.role == "coordinator":
            qs = qs.filter(workflow_state__in=[
                "coordinator_review",
                "lead_review",
                "approved",
                "rejected"
            ])

        if user.role == "lead":
            qs = qs.filter(workflow_state__in=[
                "lead_review",
                "approved",
                "rejected"
            ])

        total = qs.count()

        by_status = qs.values("workflow_state").annotate(
            count=Count("id")
        )

        return {
            "total_submissions": total,
            "status_breakdown": list(by_status)
        }

    @staticmethod
    def monthly_report(year, month):
        qs = Submission.objects.filter(
            created_at__year=year,
            created_at__month=month
        )

        return qs.values("workflow_state").annotate(count=Count("id"))

    @staticmethod
    def quarterly_report(year, quarter):
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2

        qs = Submission.objects.filter(
            created_at__year=year,
            created_at__month__gte=start_month,
            created_at__month__lte=end_month
        )

        return qs.values("workflow_state").annotate(count=Count("id"))