from django import forms
from django.forms import ModelForm
from convenient_formsets import ConvenientBaseModelFormSet

from . import models


class ContributorForm(ModelForm):
    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["person"].queryset = models.Person.site_objects(request).all()  # type: ignore
        self.fields["role"].queryset = models.PersonRole.site_objects(request).all()  # type: ignore


class RequestConvenientBaseModelFormSet(ConvenientBaseModelFormSet):
   def get_form_kwargs(self, index):
       kwargs = super().get_form_kwargs(index)
       kwargs['request'] = self.request
       return kwargs


BaseContributorFormSet = forms.modelformset_factory(
    models.Contributor,
    fields=['person', 'role'],
    form=ContributorForm,
    formset=RequestConvenientBaseModelFormSet,
    can_delete=True,
    can_order=False,
    extra=0,
    min_num=1,
    max_num=10,
    validate_min=True,
)


class ContributorFormSet(BaseContributorFormSet):
    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['request'] = self.request
        return super()._construct_form(i, **kwargs)  # type: ignore


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

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["status"].queryset = models.ResourceStatus.site_objects(request).all()  # type: ignore
        self.fields["license"].queryset = models.License.site_objects(request).all()  # type: ignore
        self.fields["groups"].queryset = models.Group.site_objects(request).all()  # type: ignore


class ResourceFiltersForm(forms.Form):
    search = forms.CharField(required=False)
    kind = forms.ChoiceField(
        choices=[('', 'All resource types')] + models.Resource.Kind.choices,  # type: ignore
        widget=forms.Select,
        required=False,
    )
    group = forms.ModelChoiceField(
        queryset=models.Group.objects.none(),
        widget=forms.Select,
        required=False,
        empty_label='All use cases'
    )
    status = forms.ModelChoiceField(
        queryset=models.ResourceStatus.objects.none(),
        widget=forms.Select,
        required=False,
        empty_label='All statuses'
    )
    organisation = forms.ModelChoiceField(
        queryset=models.Organisation.objects.none(),
        widget=forms.Select,
        required=False,
        empty_label='All organisations'
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['group'].queryset = models.Group.site_objects(request).all()  # type: ignore
        self.fields['status'].queryset = models.Group.site_objects(request).all()  # type: ignore
        self.fields['organisation'].queryset = models.Group.site_objects(request).all()  # type: ignore


class StudyDesignForm(ModelForm):

    class Meta:
        model = models.StudyDesign
        exclude = ['site']
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["license"].queryset = models.License.site_objects(request).all()  # type: ignore
        self.fields["groups"].queryset = models.Group.site_objects(request).all()  # type: ignore
