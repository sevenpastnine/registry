import functools

from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchQuery

from . import models
from . import forms


def index(request):
    return render(request, 'registry/index.html', {
        'study_designs': models.StudyDesign.site_objects(request).filter(archived=False),
        'resources': models.Resource.site_objects(request).filter(archived=False),
        'people': models.Person.site_objects(request).all(),
        'organisations': models.Organisation.site_objects(request).all(),
        'groups': models.Group.site_objects(request).all(),
    })


def people(request):
    return render(request, 'registry/people.html', {
        'people': models.Person.site_objects(request).all().select_related('user')
    })


def person(request, person_id):
    person = get_object_or_404(models.Person.site_objects(request), pk=person_id)
    return render(request, 'registry/person.html', {
        'person': person,
        'resources': models.Resource.site_objects(request).filter(archived=False, contributors__person=person),
    })


def organisations(request):
    return render(request, 'registry/organisations.html', {
        'organisations': models.Organisation.site_objects(request).all()
    })


def organisation(request, organisation_id):
    return render(request, 'registry/organisation.html', {
        'organisation': get_object_or_404(models.Organisation.site_objects(request), pk=organisation_id)
    })


def groups(request):
    return render(request, 'registry/groups.html', {
        'groups': models.Group.site_objects(request).all()
    })


def group(request, group_id):
    group = get_object_or_404(models.Group.site_objects(request), pk=group_id)
    return render(request, 'registry/group.html', {
        'group': group,
        'resources': models.Resource.site_objects(request).filter(archived=False, groups=group),
        'study_designs': models.StudyDesign.site_objects(request).filter(archived=False, groups=group),
    })


def licenses(request):
    return render(request, 'registry/licenses.html', {
        'licenses': models.License.site_objects(request).all()
    })


def license(request, license_id):
    license = get_object_or_404(models.License.site_objects(request), pk=license_id)
    return render(request, 'registry/license.html', {
        'license': license,
        'resources': models.Resource.site_objects(request).filter(archived=False, license=license),
    })


def get_resources(request, filters=None):
    queryset = models.Resource.site_objects(request).filter(archived=False).select_related('status').prefetch_related('groups')
    if not filters:
        return queryset
    else:
        if filters.get('search'):
            REMOVE_CHARS = "()|&:*!"
            MIN_QUERY_LENGTH = 2
            query_string = filters.get('search').strip().translate({ord(i): " " for i in REMOVE_CHARS}).strip()
            tokens = [token.strip() for token in query_string.split() if len(token.strip()) >= MIN_QUERY_LENGTH]
            if tokens:
                query = functools.reduce(lambda a, b: a & b, [SearchQuery(f'{token}:*', search_type='raw') for token in tokens])
                queryset = queryset.filter(Q(id__search=query) | Q(name__search=query) | Q(description__search=query))
        if filters.get('kind'):
            queryset = queryset.filter(kind=filters.get('kind'))
        if filters.get('group'):
            queryset = queryset.filter(groups=filters.get('group'))
        if filters.get('status'):
            queryset = queryset.filter(status=filters.get('status'))
        if filters.get('organisation'):
            queryset = queryset.filter(contributors__person__in=filters.get('organisation').people.all())
        return queryset


def resources(request):
    filters_form = forms.ResourceFiltersForm(request, request.GET)

    if filters_form.is_valid():
        resources = get_resources(request, filters_form.cleaned_data)
        if request.htmx and not request.htmx.boosted:
            return render(request, 'registry/partials/resources.html', {
                'resources': resources,
                'filters_form': filters_form,
            })
    else:
        resources = get_resources(request)

    return render(request, 'registry/resources.html', {
        'resources': resources,
        'filters_form': filters_form,
    })


def resource(request, resource_id):
    resource = get_object_or_404(models.Resource.site_objects(request), pk=resource_id)

    return render(request, 'registry/resource.html', {
        'resource': resource
    })


def study_designs(request):
    return render(request, 'registry/study_designs.html', {
        'study_designs': models.StudyDesign.site_objects(request).filter(archived=False)
    })


def study_design(request, study_design_id):
    study_design = get_object_or_404(models.StudyDesign.site_objects(request), pk=study_design_id)

    return render(request, 'registry/study_design.html', {
        'study_design': study_design,
        'nodes': study_design.nodes.all().prefetch_related('resources'),  # type: ignore
    })


def study_design_map(request, study_design_id):
    return render(request, 'registry/study_design_map.html', {
        'node_types': list(models.StudyDesignNodeType.site_objects(request).all().values('id', 'name', 'color', 'description')),
        'study_design': get_object_or_404(models.StudyDesign.site_objects(request), pk=study_design_id),
        'organisations': dict([(org.id, org.short_name) for org in models.Organisation.site_objects(request).all().order_by('short_name')]),
    })


# -----------------------------------------------------------------------------
# Resource editing

@transaction.atomic
def resource_add(request):
    if request.method == 'POST':
        form = forms.ResourceForm(request, request.POST, request.FILES)
        contributor_formset = forms.ContributorFormSet(request.POST, request=request, prefix='contributors')
        file_formset = forms.ResourceFileFormSet(request.POST, request.FILES, prefix='files')
        if form.is_valid() and contributor_formset.is_valid() and file_formset.is_valid():
            resource = form.save(commit=False)
            resource.site = request.site
            resource.save()
            save_contributor_formset(contributor_formset, resource)
            save_resource_file_formset(file_formset, resource)
            messages.add_message(request, messages.SUCCESS, 'A new resource has been registered.')
            return redirect('registry:resource', resource_id=resource.id)
    else:
        form = forms.ResourceForm(request)
        contributor_formset = forms.ContributorFormSet(request=request, prefix='contributors', queryset=models.Contributor.objects.none())
        file_formset = forms.ResourceFileFormSet(prefix='files', queryset=models.ResourceFile.objects.none())

    return render(request, 'registry/resource_add.html', {
        'form': form,
        'contributor_formset': contributor_formset,
        'file_formset': file_formset,
    })


@transaction.atomic
def resource_edit(request, resource_id):
    resource = get_object_or_404(models.Resource.site_objects(request), pk=resource_id)

    if request.method == 'POST':
        form = forms.ResourceForm(request, request.POST, request.FILES, instance=resource)
        contributor_formset = forms.ContributorFormSet(request.POST, request=request, prefix='contributors')
        file_formset = forms.ResourceFileFormSet(request.POST, request.FILES, prefix='files')
        if form.is_valid() and contributor_formset.is_valid() and file_formset.is_valid():
            resource = form.save()
            save_contributor_formset(contributor_formset, resource)
            save_resource_file_formset(file_formset, resource)
            messages.add_message(request, messages.SUCCESS, 'Resource has been updated.')
            return redirect('registry:resource', resource_id=resource.id)
    else:
        form = forms.ResourceForm(request, instance=resource)
        contributor_formset = forms.ContributorFormSet(
            request=request,
            prefix='contributors',
            queryset=models.Contributor.objects.filter(
                content_type=ContentType.objects.get_for_model(models.Resource),
                object_id=resource.id))
        file_formset = forms.ResourceFileFormSet(
            prefix='files',
            queryset=models.ResourceFile.objects.filter(resource=resource))

    return render(request, 'registry/resource_edit.html', {
        'resource': resource,
        'form': form,
        'contributor_formset': contributor_formset,
        'file_formset': file_formset,
    })


# -----------------------------------------------------------------------------
# Study design editing

@transaction.atomic
def study_design_add(request):
    if request.method == 'POST':
        form = forms.StudyDesignForm(request, request.POST, request.FILES)
        contributor_formset = forms.ContributorFormSet(request.POST, request=request, prefix='contributors')
        if form.is_valid() and contributor_formset.is_valid():
            study_design = form.save(commit=False)
            study_design.site = request.site
            study_design.save()
            save_contributor_formset(contributor_formset, study_design)
            messages.add_message(request, messages.SUCCESS, 'A new study design has been registered.')
            return redirect('registry:study_design_map', study_design_id=study_design.id)
    else:
        form = forms.StudyDesignForm(request)
        contributor_formset = forms.ContributorFormSet(request=request, prefix='contributors', queryset=models.Contributor.objects.none())

    return render(request, 'registry/study_design_add.html', {
        'form': form,
        'contributor_formset': contributor_formset,
    })


@transaction.atomic
def study_design_edit(request, study_design_id):
    study_design = get_object_or_404(models.StudyDesign.site_objects(request), pk=study_design_id)

    if request.method == 'POST':
        form = forms.StudyDesignForm(request, request.POST, request.FILES, instance=study_design)
        contributor_formset = forms.ContributorFormSet(request.POST, request=request, prefix='contributors')
        if form.is_valid() and contributor_formset.is_valid():
            study_design = form.save()
            save_contributor_formset(contributor_formset, study_design)
            messages.add_message(request, messages.SUCCESS, 'Study design has been updated.')
            return redirect('registry:study_design', study_design_id=study_design.id)
    else:
        form = forms.StudyDesignForm(request, instance=study_design)
        contributor_formset = forms.ContributorFormSet(
            request=request,
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


def save_resource_file_formset(formset, resource):
    for form in formset:
        if form.is_valid():
            if form.cleaned_data.get('DELETE') and form.instance.pk:
                form.instance.delete()
            else:
                if form.cleaned_data.get('file'):
                    file = form.save(commit=False)
                    file.resource = resource
                    file.save()

# -----------------------------------------------------------------------------
