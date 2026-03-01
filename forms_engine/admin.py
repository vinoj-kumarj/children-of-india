from django.contrib import admin
from .models import Form, FormVersion, FormField


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1


class FormVersionInline(admin.TabularInline):
    model = FormVersion
    extra = 1


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ("id", "initiative", "is_active", "created_at")
    inlines = [FormVersionInline]


@admin.register(FormVersion)
class FormVersionAdmin(admin.ModelAdmin):
    list_display = ("form", "version_number", "is_published")
    inlines = [FormFieldInline]