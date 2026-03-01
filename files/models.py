import uuid
from django.db import models
from django.conf import settings


class UploadedFile(models.Model):
    FILE_TYPES = (
        ("form_scan", "Offline Form Scan"),
        ("image_header", "Form Header Image"),
        ("supporting_doc", "Supporting Document"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    file = models.FileField(upload_to="uploads/")
    file_type = models.CharField(max_length=50, choices=FILE_TYPES)

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.file.name)


class OCRMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    uploaded_file = models.OneToOneField(UploadedFile, on_delete=models.CASCADE)

    extracted_text = models.TextField(blank=True, null=True)
    extracted_json = models.JSONField(blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)

    processed_at = models.DateTimeField(auto_now_add=True)