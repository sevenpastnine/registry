from django import forms

from . import models


class OrganisationAdminForm(forms.ModelForm):
    class Meta:
        model = models.Organisation
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        sites = set(cleaned_data.get("sites", models.Site.objects.none()).values_list("id", flat=True))
        people = cleaned_data.get("people", [])

        for person in people:
            person_sites = set(person.sites.values_list("id", flat=True))
            if not person_sites.intersection(sites):
                self.add_error('people', f"Person {person} is not on the same site as the organisation.")

        return cleaned_data


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        site = cleaned_data.get("site", None)

        if site is not None:
            people = cleaned_data.get("people", [])
            for person in people:
                if site not in person.sites.all():
                    self.add_error('people', f"Person {person} is not on the same site as the group.")

        return cleaned_data


class ResourceAdminForm(forms.ModelForm):
    class Meta:
        model = models.Resource
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        site = cleaned_data.get("site", None)

        if site is not None:
            status = cleaned_data.get("status")
            if status is not None and status.site != site:
                self.add_error('status', "Status is not on the same site as the resource.")

            license = cleaned_data.get("license")
            if license is not None and site not in license.sites.all():
                self.add_error('license', "License is not on the same site as the resource.")

            for group in cleaned_data.get("groups", models.Group.objects.none()).select_related("site"):
                if site != group.site:
                    self.add_error('groups', f"Group {group} is not on the same site as the resource.")

        return cleaned_data


class StudyDesignAdminForm(forms.ModelForm):
    class Meta:
        model = models.StudyDesign
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        site = cleaned_data.get("site", None)

        if site is not None:
            license = cleaned_data.get("license")
            if license is not None and site not in license.sites.all():
                self.add_error('license', "License is not on the same site as the resource.")

            for group in cleaned_data.get("groups", models.Group.objects.none()).select_related("site"):
                if site != group.site:
                    self.add_error('groups', f"Group {group} is not on the same site as the resource.")

        return cleaned_data
