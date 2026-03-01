from django.urls import path
from .views import submit_submission

urlpatterns = [
    path("submit/<uuid:submission_id>/", submit_submission, name="submit_submission"),
]