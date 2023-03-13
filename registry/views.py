from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType

from . import models
from . import forms


def index(request):
    return render(request, 'registry/index.html', {
        'study_designs': models.StudyDesign.objects.all(),
        'resources': models.Resource.objects.all(),
        'people': models.Person.objects.all(),
        'organisations': models.Organisation.objects.all(),
        'groups': models.Group.objects.all(),
    })


def people(request):
    return render(request, 'registry/people.html', {
        'people': models.Person.objects.all()
    })


def person(request, person_id):
    return render(request, 'registry/person.html', {
        'person': get_object_or_404(models.Person, pk=person_id)
    })


def organisations(request):
    return render(request, 'registry/organisations.html', {
        'organisations': models.Organisation.objects.all()
    })


def organisation(request, organisation_id):
    return render(request, 'registry/organisation.html', {
        'organisation': get_object_or_404(models.Organisation, pk=organisation_id)
    })


def groups(request):
    return render(request, 'registry/groups.html', {
        'groups': models.Group.objects.all()
    })


def group(request, group_id):
    return render(request, 'registry/group.html', {
        'group': get_object_or_404(models.Group, pk=group_id)
    })


def licenses(request):
    return render(request, 'registry/licenses.html', {
        'licenses': models.License.objects.all()
    })


def license(request, license_id):
    return render(request, 'registry/license.html', {
        'license': get_object_or_404(models.License, pk=license_id)
    })


def get_resources(filters=None):
    queryset = models.Resource.objects.all()
    if not filters:
        return queryset
    else:
        if filters.get('kind'):
            queryset = queryset.filter(kind=filters.get('kind'))
        if filters.get('group'):
            queryset = queryset.filter(groups=filters.get('group'))
        if filters.get('status'):
            queryset = queryset.filter(status=filters.get('status'))
        return queryset


def resources(request):
    filters_form = forms.ResourceFiltersForm(request.GET)

    if filters_form.is_valid():
        resources = get_resources(filters_form.cleaned_data)
        if request.htmx:
            return render(request, 'registry/partials/resources.html', {
                'resources': resources,
                'filters_form': filters_form,
            })
    else:
        resources = get_resources()

    return render(request, 'registry/resources.html', {
        'resources': resources,
        'filters_form': filters_form,
    })


def resource(request, resource_id):
    return render(request, 'registry/resource.html', {
        'resource': get_object_or_404(models.Resource, pk=resource_id)
    })


def study_designs(request):
    return render(request, 'registry/study_designs.html', {
        'study_designs': models.StudyDesign.objects.all()
    })


def study_design(request, study_design_id):
    return render(request, 'registry/study_design.html', {
        'study_design': get_object_or_404(models.StudyDesign, pk=study_design_id)
    })


# -----------------------------------------------------------------------------
# Resource editing

def resource_add(request):
    if request.method == 'POST':
        form = forms.ResourceForm(request.POST, request.FILES)
        contributor_formset = forms.ContributorFormSet(request.POST, prefix='contributors')
        if form.is_valid() and contributor_formset.is_valid():
            resource = form.save()
            save_contributor_formset(contributor_formset, resource)
            messages.add_message(request, messages.SUCCESS, 'A new resource has been registered.')
            return redirect('registry:resource', resource_id=resource.id)
    else:
        form = forms.ResourceForm()
        contributor_formset = forms.ContributorFormSet(prefix='contributors', queryset=models.Contributor.objects.none())

    return render(request, 'registry/resource_add.html', {
        'form': form,
        'contributor_formset': contributor_formset,
    })


def resource_edit(request, resource_id):
    resource = get_object_or_404(models.Resource, pk=resource_id)

    if request.method == 'POST':
        form = forms.ResourceForm(request.POST, request.FILES, instance=resource)
        contributor_formset = forms.ContributorFormSet(request.POST, prefix='contributors')
        if form.is_valid() and contributor_formset.is_valid():
            resource = form.save()
            save_contributor_formset(contributor_formset, resource)
            messages.add_message(request, messages.SUCCESS, 'Resource has been updated.')
            return redirect('registry:resource', resource_id=resource.id)
    else:
        form = forms.ResourceForm(instance=resource)
        contributor_formset = forms.ContributorFormSet(
            prefix='contributors',
            queryset=models.Contributor.objects.filter(
                content_type=ContentType.objects.get_for_model(models.Resource),
                object_id=resource.id))

    return render(request, 'registry/resource_edit.html', {
        'resource': resource,
        'form': form,
        'contributor_formset': contributor_formset,
    })


# -----------------------------------------------------------------------------
# Study design editing

def study_design_add(request):
    if request.method == 'POST':
        form = forms.StudyDesignForm(request.POST, request.FILES)
        contributor_formset = forms.ContributorFormSet(request.POST, prefix='contributors')
        if form.is_valid() and contributor_formset.is_valid():
            study_design = form.save()
            save_contributor_formset(contributor_formset, study_design)
            messages.add_message(request, messages.SUCCESS, 'A new study design has been registered.')
            return redirect('registry:study_design', study_design_id=study_design.id)
    else:
        form = forms.StudyDesignForm()
        contributor_formset = forms.ContributorFormSet(prefix='contributors', queryset=models.Contributor.objects.none())

    return render(request, 'registry/study_design_add.html', {
        'form': form,
        'contributor_formset': contributor_formset,
    })


def study_design_edit(request, study_design_id):
    study_design = get_object_or_404(models.StudyDesign, pk=study_design_id)

    if request.method == 'POST':
        form = forms.StudyDesignForm(request.POST, request.FILES, instance=study_design)
        contributor_formset = forms.ContributorFormSet(request.POST, prefix='contributors')
        if form.is_valid() and contributor_formset.is_valid():
            study_design = form.save()
            save_contributor_formset(contributor_formset, study_design)
            messages.add_message(request, messages.SUCCESS, 'Study design has been updated.')
            return redirect('registry:study_design', study_design_id=study_design.id)
    else:
        form = forms.StudyDesignForm(instance=study_design)
        contributor_formset = forms.ContributorFormSet(
            prefix='contributors',
            queryset=models.Contributor.objects.filter(
                content_type=ContentType.objects.get_for_model(models.StudyDesign),
                object_id=study_design.id))

    return render(request, 'registry/study_design_edit.html', {
        'study_design': study_design,
        'form': form,
        'contributor_formset': contributor_formset,
    })


# -----------------------------------------------------------------------------
# Helpers

def save_contributor_formset(formset, content_object):
    content_type = ContentType.objects.get_for_model(content_object.__class__)
    models.Contributor.objects.filter(content_type=content_type, object_id=content_object.id).delete()

    for form in formset:
        if form.is_valid():
            if form.cleaned_data.get('DELETE') and form.instance.pk:
                pass
            else:
                contributor = form.save(commit=False)
                models.Contributor.objects.update_or_create(person=contributor.person, role=contributor.role, content_type=content_type, object_id=content_object.id)
