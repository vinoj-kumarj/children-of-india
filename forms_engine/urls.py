from django.urls import path
from .views import fill_form, list_forms

urlpatterns = [
    path("", list_forms, name="list_forms"),
    path("<uuid:version_id>/fill/", fill_form, name="fill_form"),
]