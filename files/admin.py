from django.contrib import admin
from .models import UploadedFile, OCRMetadata


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("file", "file_type", "uploaded_by", "uploaded_at")


@admin.register(OCRMetadata)
class OCRMetadataAdmin(admin.ModelAdmin):
    list_display = ("uploaded_file", "confidence_score", "processed_at")