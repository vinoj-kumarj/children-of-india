from django.contrib import admin
from .models import Initiative, District, Village, UserGeography


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ("id", "is_active", "created_at")


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ("id", "district")


@admin.register(UserGeography)
class UserGeographyAdmin(admin.ModelAdmin):
    list_display = ("user", "district", "village")