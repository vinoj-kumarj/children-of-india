from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .services import ReportService
from django.utils import timezone
from submissions.models import Submission
from django.db.models import Count, Q, F, Case, When, Value, CharField, Avg
from django.db.models.functions import TruncWeek
from datetime import timedelta
from workflow.models import WorkflowAudit
from accounts.models import User
from forms_engine.models import Form, FormVersion
from initiatives.models import Initiative
from django.http import JsonResponse
import json
from django.views.decorators.http import require_http_methods


@login_required
def dashboard(request):
    if request.user.role == "coordinator":
        return redirect("coordinator_dashboard")

    if request.user.role == "lead":
        return redirect("lead_dashboard")

    submissions = Submission.objects.filter(user=request.user)

    return render(request, "reports/dashboard.html", {
        "submissions": submissions
    })


@login_required
def monthly_report_view(request):
    now = timezone.now()
    report = ReportService.monthly_report(now.year, now.month)
    return render(request, "reports/monthly.html", {"report": report})


@login_required
def quarterly_report_view(request):
    now = timezone.now()
    quarter = (now.month - 1) // 3 + 1
    report = ReportService.quarterly_report(now.year, quarter)
    return render(request, "reports/quarterly.html", {"report": report})


@login_required
def analytics_dashboard(request):
    """Main analytics dashboard with all metrics and charts"""
    
    # Executive Summary Metrics
    total_initiatives = Initiative.objects.filter(is_active=True).count()
    total_submissions = Submission.objects.count()
    field_coordinators = User.objects.filter(role='field', is_active=True).count()
    
    approved_count = Submission.objects.filter(workflow_state='approved').count()
    rejected_count = Submission.objects.filter(workflow_state='rejected').count()
    coordinator_review_count = Submission.objects.filter(workflow_state='coordinator_review').count()
    lead_review_count = Submission.objects.filter(workflow_state='lead_review').count()
    draft_count = Submission.objects.filter(workflow_state='draft').count()
    submitted_count = Submission.objects.filter(workflow_state='submitted').count()
    
    approval_rate = (approved_count / total_submissions * 100) if total_submissions > 0 else 0
    
    # Submissions by Initiative
    initiatives_list = Initiative.objects.filter(is_active=True)
    submissions_by_initiative = []
    for initiative in initiatives_list:
        total = Submission.objects.filter(form_version__form__initiative_id=initiative.id).count()
        approved = Submission.objects.filter(form_version__form__initiative_id=initiative.id, workflow_state='approved').count()
        rejected = Submission.objects.filter(form_version__form__initiative_id=initiative.id, workflow_state='rejected').count()
        pending = Submission.objects.filter(form_version__form__initiative_id=initiative.id, workflow_state__in=['coordinator_review', 'lead_review']).count()
        draft = Submission.objects.filter(form_version__form__initiative_id=initiative.id, workflow_state='draft').count()
        
        submissions_by_initiative.append({
            'id': str(initiative.id),
            'name_json': initiative.name_json,
            'total': total,
            'approved': approved,
            'rejected': rejected,
            'pending': pending,
            'draft': draft
        })
    
    # Field Coordinator Performance
    coordinators = User.objects.filter(role='field', is_active=True)
    field_coordinators_stats = []
    for coordinator in coordinators:
        total_submissions = Submission.objects.filter(user_id=coordinator.id).count()
        approved_submissions = Submission.objects.filter(user_id=coordinator.id, workflow_state='approved').count()
        rejected_submissions = Submission.objects.filter(user_id=coordinator.id, workflow_state='rejected').count()
        draft_submissions = Submission.objects.filter(user_id=coordinator.id, workflow_state='draft').count()
        
        approval_rate = (approved_submissions / total_submissions * 100) if total_submissions > 0 else 0
        
        field_coordinators_stats.append({
            'id': str(coordinator.id),
            'full_name': coordinator.get_full_name(),
            'email': coordinator.email,
            'district': coordinator.district or 'N/A',
            'total_submissions': total_submissions,
            'approved_submissions': approved_submissions,
            'rejected_submissions': rejected_submissions,
            'draft_submissions': draft_submissions,
            'approval_rate': round(approval_rate, 1)
        })
    
    # Submissions by Workflow State (for pie chart)
    submissions_by_state = Submission.objects.values('workflow_state').annotate(count=Count('id')).order_by('workflow_state')
    
    # Recent Activity Audit Trail
    recent_audits = WorkflowAudit.objects.select_related(
        'submission', 'user', 'submission__form_version__form'
    ).order_by('-created_at')[:10]
    
    # Pending Submissions Timeline
    pending_submissions = Submission.objects.filter(
        workflow_state__in=['coordinator_review', 'lead_review', 'submitted']
    ).select_related(
        'user', 'form_version__form'
    ).order_by('submitted_at')
    
    # Add time in system for each
    for submission in pending_submissions:
        submission.time_in_system = timezone.now() - (submission.submitted_at or submission.created_at)
        submission.days_pending = submission.time_in_system.days
        if submission.days_pending > 7:
            submission.priority = 'URGENT'
        elif submission.days_pending > 3:
            submission.priority = 'ATTENTION NEEDED'
        else:
            submission.priority = 'ON TRACK'
    
    # Approval Trends by Week
    two_weeks_ago = timezone.now() - timedelta(days=14)
    weekly_trends = Submission.objects.filter(
        created_at__gte=two_weeks_ago
    ).annotate(
        week=TruncWeek('created_at')
    ).values('week').annotate(
        total=Count('id'),
        approved=Count('id', filter=Q(workflow_state='approved')),
        rejected=Count('id', filter=Q(workflow_state='rejected'))
    ).order_by('week')
    
    # Data Quality Metrics
    forms_quality = []
    for form_version in FormVersion.objects.filter(is_published=True).select_related('form'):
        submission_count = Submission.objects.filter(form_version_id=form_version.id).count()
        forms_quality.append({
            'form_id': str(form_version.form_id),
            'form_name': form_version.form.name_json.get('en', 'Unknown'),
            'total_submissions': submission_count,
            'avg_completeness': 85  # Placeholder
        })
    
    # Role Distribution
    role_distribution = User.objects.filter(
        is_active=True
    ).values('role').annotate(
        count=Count('id'),
        active_count=Count('id', filter=Q(is_approved=True))
    )
    
    # Submission Status Funnel
    funnel_data = {
        'total': total_submissions,
        'submitted': submitted_count + coordinator_review_count + lead_review_count + approved_count + rejected_count,
        'in_review': coordinator_review_count + lead_review_count,
        'finalized': approved_count + rejected_count
    }
    
    context = {
        'total_initiatives': total_initiatives,
        'total_submissions': total_submissions,
        'field_coordinators': field_coordinators,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'coordinator_review_count': coordinator_review_count,
        'lead_review_count': lead_review_count,
        'draft_count': draft_count,
        'submitted_count': submitted_count,
        'approval_rate': round(approval_rate, 1),
        
        'submissions_by_initiative': list(submissions_by_initiative),
        'field_coordinators_stats': list(field_coordinators_stats),
        'submissions_by_state': list(submissions_by_state),
        'recent_audits': recent_audits,
        'pending_submissions': pending_submissions,
        'weekly_trends': list(weekly_trends),
        'forms_quality': forms_quality,
        'role_distribution': list(role_distribution),
        'funnel_data': funnel_data,
    }
    
    return render(request, 'reports/analytics_dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def get_chart_data(request, chart_type):
    """API endpoint to get chart data as JSON"""
    
    if chart_type == 'submissions_by_state':
        data = Submission.objects.values('workflow_state').annotate(count=Count('id'))
        states = {
            'draft': 'Draft',
            'submitted': 'Submitted',
            'coordinator_review': 'Coordinator Review',
            'lead_review': 'Lead Review',
            'approved': 'Approved',
            'rejected': 'Rejected',
            'resubmission': 'Resubmission'
        }
        
        labels = [states.get(item['workflow_state'], item['workflow_state']) for item in data]
        values = [item['count'] for item in data]
        colors = ['#FFC107', '#0D6EFD', '#0DCAF0', '#6F42C1', '#28A745', '#DC3545', '#FD7E14']
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'data': values,
                'backgroundColor': colors[:len(values)],
                'borderColor': '#fff',
                'borderWidth': 2
            }]
        })
    
    elif chart_type == 'submissions_by_initiative':
        initiatives = Initiative.objects.filter(is_active=True)
        labels = []
        approved_data = []
        rejected_data = []
        
        for init in initiatives:
            approved = Submission.objects.filter(form_version__form__initiative_id=init.id, workflow_state='approved').count()
            rejected = Submission.objects.filter(form_version__form__initiative_id=init.id, workflow_state='rejected').count()
            
            labels.append(init.name_json.get('en', 'Unknown'))
            approved_data.append(approved)
            rejected_data.append(rejected)
        
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Approved',
                    'data': approved_data,
                    'backgroundColor': '#28A745',
                    'borderColor': '#fff',
                    'borderWidth': 1
                },
                {
                    'label': 'Rejected',
                    'data': rejected_data,
                    'backgroundColor': '#DC3545',
                    'borderColor': '#fff',
                    'borderWidth': 1
                }
            ]
        })
    
    elif chart_type == 'approval_trend':
        two_weeks_ago = timezone.now() - timedelta(days=14)
        trends = Submission.objects.filter(
            created_at__gte=two_weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            total=Count('id'),
            approved=Count('id', filter=Q(workflow_state='approved')),
            rejected=Count('id', filter=Q(workflow_state='rejected'))
        ).order_by('week')
        
        labels = []
        total_data = []
        approved_data = []
        rejected_data = []
        
        for trend in trends:
            if trend['week']:
                labels.append(trend['week'].strftime('%b %d'))
                total_data.append(trend['total'])
                approved_data.append(trend['approved'])
                rejected_data.append(trend['rejected'])
        
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Total Submissions',
                    'data': total_data,
                    'borderColor': '#0D6EFD',
                    'backgroundColor': 'rgba(13, 110, 253, 0.1)',
                    'tension': 0.4,
                    'fill': True,
                    'borderWidth': 2
                },
                {
                    'label': 'Approved',
                    'data': approved_data,
                    'borderColor': '#28A745',
                    'backgroundColor': 'rgba(40, 167, 69, 0.1)',
                    'tension': 0.4,
                    'fill': True,
                    'borderWidth': 2
                },
                {
                    'label': 'Rejected',
                    'data': rejected_data,
                    'borderColor': '#DC3545',
                    'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                    'tension': 0.4,
                    'fill': True,
                    'borderWidth': 2
                }
            ]
        })
    
    elif chart_type == 'coordinator_performance':
        coordinators = User.objects.filter(role='field', is_active=True)
        labels = []
        total_data = []
        approved_data = []
        
        for coord in coordinators:
            total = Submission.objects.filter(user_id=coord.id).count()
            approved = Submission.objects.filter(user_id=coord.id, workflow_state='approved').count()
            
            labels.append(coord.get_full_name())
            total_data.append(total)
            approved_data.append(approved)
        
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Total Submissions',
                    'data': total_data,
                    'backgroundColor': '#0D6EFD',
                    'borderColor': '#fff',
                    'borderWidth': 1
                },
                {
                    'label': 'Approved',
                    'data': approved_data,
                    'backgroundColor': '#28A745',
                    'borderColor': '#fff',
                    'borderWidth': 1
                }
            ]
        })
    
    elif chart_type == 'workflow_funnel':
        total = Submission.objects.count()
        submitted = Submission.objects.filter(submitted_at__isnull=False).count()
        in_review = Submission.objects.filter(workflow_state__in=['coordinator_review', 'lead_review']).count()
        finalized = Submission.objects.filter(workflow_state__in=['approved', 'rejected']).count()
        
        return JsonResponse({
            'labels': ['All Started', 'Submitted', 'In Review', 'Finalized'],
            'datasets': [{
                'data': [total, submitted, in_review, finalized],
                'backgroundColor': ['#0D6EFD', '#0DCAF0', '#FFC107', '#28A745'],
                'borderColor': '#fff',
                'borderWidth': 2
            }]
        })
    
    return JsonResponse({'error': 'Invalid chart type'}, status=400)


@login_required
def get_submission_details(request, submission_id):
    """Get submission details for modal popup"""
    try:
        submission = Submission.objects.select_related(
            'user', 'form_version__form__initiative'
        ).get(id=submission_id)
        
        audits = WorkflowAudit.objects.filter(
            submission_id=submission_id
        ).select_related('user').order_by('created_at')
        
        data = {
            'id': str(submission.id),
            'form_name': submission.form_version.form.name_json.get('en', 'Unknown'),
            'submitted_by': submission.user.get_full_name(),
            'initiative': submission.form_version.form.initiative.name_json.get('en', 'Unknown'),
            'state': submission.workflow_state,
            'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
            'created_at': submission.created_at.isoformat(),
            'audits': [
                {
                    'user': audit.user.get_full_name(),
                    'action': audit.action,
                    'from_state': audit.from_state,
                    'to_state': audit.to_state,
                    'created_at': audit.created_at.isoformat()
                }
                for audit in audits
            ]
        }
        
        return JsonResponse(data)
    except Submission.DoesNotExist:
        return JsonResponse({'error': 'Submission not found'}, status=404)