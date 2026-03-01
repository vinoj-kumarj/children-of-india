from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("monthly/", views.monthly_report_view, name="monthly_report"),
    path("quarterly/", views.quarterly_report_view, name="quarterly_report"),
    path("analytics/", views.analytics_dashboard, name="analytics_dashboard"),
    path("api/chart/<str:chart_type>/", views.get_chart_data, name="get_chart_data"),
    path("api/submission/<uuid:submission_id>/", views.get_submission_details, name="get_submission_details"),
]