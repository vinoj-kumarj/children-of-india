from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from initiatives.models import Initiative
from forms_engine.models import Form, FormVersion
from submissions.models import Submission

User = get_user_model()


class FieldCoordinatorSubmissionTests(TestCase):
    def setUp(self):
        # create a field user
        self.user = User.objects.create_user(
            username="fielduser",
            email="field@example.com",
            password="pass",
            role="field",
        )

        # create minimal form hierarchy
        self.initiative = Initiative.objects.create(name_json={"en": "Test"})
        form = Form.objects.create(initiative=self.initiative, name_json={"en": "F"})
        self.form_version = FormVersion.objects.create(
            form=form,
            version_number=1,
            schema_json={},
            is_published=True,
        )

        # create a draft submission belonging to user
        self.submission = Submission.objects.create(
            form_version=self.form_version,
            user=self.user,
            workflow_state="draft",
        )

    def test_history_page_shows_submit_button(self):
        self.client.login(email="field@example.com", password="pass")
        url = reverse("field_submissions")
        resp = self.client.get(url)
        self.assertContains(resp, "Submit")
        # ensure the link points to the correct URL
        expected_link = reverse("submit_submission", args=[self.submission.id])
        self.assertIn(expected_link, resp.content.decode())

    def test_detail_page_shows_submit_form(self):
        self.client.login(email="field@example.com", password="pass")
        url = reverse("field_submission_detail", args=[self.submission.id])
        resp = self.client.get(url)
        self.assertContains(resp, "Submit to Coordinator")

    def test_submitting_changes_state(self):
        self.client.login(email="field@example.com", password="pass")
        submit_url = reverse("submit_submission", args=[self.submission.id])
        resp = self.client.post(submit_url)
        # after submission should redirect somewhere (dashboard)
        self.assertEqual(resp.status_code, 302)
        self.submission.refresh_from_db()
        # transition should move to coordinator_review
        self.assertEqual(self.submission.workflow_state, "coordinator_review")

