import uuid
from django.db import models
from initiatives.models import Initiative


class Form(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE)

    name_json = models.JSONField()
    description_json = models.JSONField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_json.get("en", "Form")


class FormVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="versions")

    version_number = models.IntegerField()
    schema_json = models.JSONField()

    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("form", "version_number")

    def __str__(self):
        return f"{self.form} v{self.version_number}"


class FormField(models.Model):
    FIELD_TYPES = (
        ("text", "Text"),
        ("number", "Number"),
        ("date", "Date"),
        ("select", "Select"),
        ("textarea", "Textarea"),
        ("image", "Image"),
        ("file", "File"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    form_version = models.ForeignKey(FormVersion, on_delete=models.CASCADE, related_name="fields")

    field_key = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)

    label_json = models.JSONField()
    placeholder_json = models.JSONField(blank=True, null=True)
    help_text_json = models.JSONField(blank=True, null=True)

    validation_json = models.JSONField(blank=True, null=True)
    options_json = models.JSONField(blank=True, null=True)

    order_index = models.IntegerField(default=0)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return self.field_key