from django.core.exceptions import ValidationError
from django import forms
from django.forms import ModelForm
from convenient_formsets import ConvenientBaseModelFormSet

from . import models


ContributorFormSet = forms.modelformset_factory(
    models.Contributor,
    fields=['person', 'role'],
    formset=ConvenientBaseModelFormSet,
    can_delete=True,
    can_order=False,
    extra=0,
    min_num=1,
    max_num=10,
    validate_min=True,
)


class ResourceForm(ModelForm):
    kind = forms.ChoiceField(label='Type of resource', choices=models.Resource.Kind.choices, widget=forms.RadioSelect)

    class Meta:
        model = models.Resource
        fields = '__all__'
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_link = cleaned_data.get('data_link', '')
        data_file = cleaned_data.get('data_file', '')

        if data_link and data_file:
            raise ValidationError('Please provide either a link to data or a file containing data, but not both.')


class ResourceFiltersForm(forms.Form):
    kind = forms.ChoiceField(
        choices=[(None, 'Resource type')] + models.Resource.Kind.choices,
        widget=forms.Select,
        required=False,
    )
    group = forms.ModelChoiceField(
        queryset=models.Group.objects.all(),
        widget=forms.Select,
        required=False,
        empty_label='Use case'
    )
    status = forms.ModelChoiceField(
        queryset=models.ResourceStatus.objects.all(),
        widget=forms.Select,
        required=False,
        empty_label='Status'
    )


class StudyDesignForm(ModelForm):

    class Meta:
        model = models.StudyDesign
        fields = '__all__'
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }
