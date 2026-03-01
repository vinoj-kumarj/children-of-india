from django.urls import path
from .views import (
    coordinator_dashboard,
    coordinator_review,
    lead_dashboard,
    lead_review,
    field_coordinator_submissions,
    field_coordinator_submission_detail
)

urlpatterns = [
    path("coordinator/", coordinator_dashboard, name="coordinator_dashboard"),
    path("coordinator/<uuid:submission_id>/", coordinator_review, name="coordinator_review"),
    path("lead/", lead_dashboard, name="lead_dashboard"),
    path("lead/<uuid:submission_id>/", lead_review, name="lead_review"),
    path("field/submissions/", field_coordinator_submissions, name="field_submissions"),
    path("field/submissions/<uuid:submission_id>/", field_coordinator_submission_detail, name="field_submission_detail"),
]