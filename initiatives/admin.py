from django.contrib import admin
from django import forms
from .models import Initiative, District, Village, UserGeography


class InitiativeForm(forms.ModelForm):
    name_en = forms.CharField(label="Name (EN)")
    description_en = forms.CharField(label="Description (EN)", widget=forms.Textarea, required=False)

    class Meta:
        model = Initiative
        fields = ("name_en", "description_en", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if isinstance(self.instance.name_json, dict):
                self.initial["name_en"] = self.instance.name_json.get("en", "")
            if isinstance(self.instance.description_json, dict):
                self.initial["description_en"] = self.instance.description_json.get("en", "")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.name_json = {"en": self.cleaned_data["name_en"]}
        instance.description_json = {"en": self.cleaned_data["description_en"]}
        if commit:
            instance.save()
        return instance


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    form = InitiativeForm
    list_display = ("id", "name_with_id", "is_active", "created_at")
    list_display_links = ("id", "name_with_id")

    def name_with_id(self, obj):
        name = obj.name_json.get("en", "Initiative") if isinstance(obj.name_json, dict) else "Initiative"
        return f"{name} - {obj.id}"
    name_with_id.short_description = "Initiative (Name - ID)"


class DistrictForm(forms.ModelForm):
    name_en = forms.CharField(label="Name (EN)")

    class Meta:
        model = District
        fields = ("name_en",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if isinstance(self.instance.name_json, dict):
                self.initial["name_en"] = self.instance.name_json.get("en", "")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.name_json = {"en": self.cleaned_data["name_en"]}
        if commit:
            instance.save()
        return instance


class VillageForm(forms.ModelForm):
    name_en = forms.CharField(label="Name (EN)")

    class Meta:
        model = Village
        fields = ("district", "name_en")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if isinstance(self.instance.name_json, dict):
                self.initial["name_en"] = self.instance.name_json.get("en", "")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.name_json = {"en": self.cleaned_data["name_en"]}
        if commit:
            instance.save()
        return instance


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    form = DistrictForm
    list_display = ("id", "get_name_en")

    def get_name_en(self, obj):
        return obj.name_json.get("en", "District") if isinstance(obj.name_json, dict) else "District"
    get_name_en.short_description = "Name (EN)"


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    form = VillageForm
    list_display = ("id", "district", "get_name_en")

    def get_name_en(self, obj):
        return obj.name_json.get("en", "Village") if isinstance(obj.name_json, dict) else "Village"
    get_name_en.short_description = "Name (EN)"


@admin.register(UserGeography)
class UserGeographyAdmin(admin.ModelAdmin):
    list_display = ("user", "district", "village")