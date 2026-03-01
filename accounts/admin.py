from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "is_approved", "is_active")
    list_filter = ("role", "is_approved")
    search_fields = ("email",)