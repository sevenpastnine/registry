from django import forms
from django.forms import ModelForm
from convenient_formsets import ConvenientBaseModelFormSet

from . import models


class ContributorForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["person"].queryset = models.Person.site_objects.all()  # type: ignore
        self.fields["role"].queryset = models.PersonRole.site_objects.all()  # type: ignore


ContributorFormSet = forms.modelformset_factory(
    models.Contributor,
    fields=['person', 'role'],
    form=ContributorForm,
    formset=ConvenientBaseModelFormSet,
    can_delete=True,
    can_order=False,
    extra=0,
    min_num=1,
    max_num=10,
    validate_min=True,
)


ResourceFileFormSet = forms.modelformset_factory(
    models.ResourceFile,
    fields=['name', 'file'],
    formset=ConvenientBaseModelFormSet,
    can_delete=True,
    can_order=False,
    extra=0,
    min_num=0,
    max_num=100
)


class ResourceForm(ModelForm):
    kind = forms.ChoiceField(label='Type of resource', choices=models.Resource.Kind.choices, widget=forms.RadioSelect)

    class Meta:
        model = models.Resource
        exclude = ['site']
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["status"].queryset = models.ResourceStatus.site_objects.all()  # type: ignore
        self.fields["license"].queryset = models.License.site_objects.all()  # type: ignore
        self.fields["groups"].queryset = models.Group.site_objects.all()  # type: ignore


class ResourceFiltersForm(forms.Form):
    search = forms.CharField(required=False)
    kind = forms.ChoiceField(
        choices=[('', 'All resource types')] + models.Resource.Kind.choices,  # type: ignore
        widget=forms.Select,
        required=False,
    )
    group = forms.ModelChoiceField(
        queryset=models.Group.site_objects.all(),
        widget=forms.Select,
        required=False,
        empty_label='All use cases'
    )
    status = forms.ModelChoiceField(
        queryset=models.ResourceStatus.site_objects.all(),
        widget=forms.Select,
        required=False,
        empty_label='All statuses'
    )
    organisation = forms.ModelChoiceField(
        queryset=models.Organisation.site_objects.all(),
        widget=forms.Select,
        required=False,
        empty_label='All organisations'
    )


class StudyDesignForm(ModelForm):

    class Meta:
        model = models.StudyDesign
        exclude = ['site']
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["license"].queryset = models.License.site_objects.all()  # type: ignore
        self.fields["groups"].queryset = models.Group.site_objects.all()  # type: ignore
