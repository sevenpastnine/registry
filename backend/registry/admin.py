import os

from django.contrib import admin
from django.urls import path
from django.contrib.contenttypes.admin import GenericTabularInline

from import_export import resources
from import_export.admin import ExportActionModelAdmin

from adminsortable2.admin import SortableAdminMixin

from . import models
from . import admin_forms as forms
from . import admin_views as views


@admin.register(models.Project)
class Project(admin.ModelAdmin):
    list_display = ['name', 'domain']
    list_display_links = ['name']


@admin.register(models.License)
class License(admin.ModelAdmin):
    list_display = ['name', 'url']
    list_display_links = ['name']
    list_filter = ['sites']
    filter_horizontal = ['sites']


@admin.register(models.Person)
class Person(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'orcid', 'email']
    list_display_links = ['email']
    list_filter = ['sites', 'organisations', 'groups']
    autocomplete_fields = ['user']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    filter_horizontal = ['sites']

    def import_people(self, request):
        return views.import_people(self, request)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-people/', self.admin_site.admin_view(self.import_people), name='import-people'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['import_url'] = 'import-people/'
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(models.PersonRole)
class PersonRole(admin.ModelAdmin):
    list_display = ['name', 'site']
    list_display_links = ['name']
    list_filter = ['site']


@admin.register(models.Organisation)
class Organisation(admin.ModelAdmin):
    list_display = ['ror', 'short_name', 'name']
    list_display_links = ['name']
    list_filter = ['sites']
    search_fields = ['ror', 'short_name', 'name']
    filter_horizontal = ['sites', 'people']
    form = forms.OrganisationAdminForm


@admin.register(models.Group)
class Group(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    list_filter = ['site']
    filter_horizontal = ['people']
    form = forms.GroupAdminForm


class ContributorInline(GenericTabularInline):
    model = models.Contributor
    extra = 0


@admin.register(models.ResourceStatus)
class ResourceStatus(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'site']
    list_display_links = ['name']
    list_filter = ['site']


class ResourceFileInline(admin.TabularInline):
    model = models.ResourceFile
    extra = 0


class ResourceResource(resources.ModelResource):

    class Meta:
        model = models.Resource
        fields = [
            'name',
            'kind',
            'status__name',
            'license__name',
            'groups',
            'data_link',
        ]

    def dehydrate_groups(self, obj):
        if obj.groups.all():
            return "\n".join([group.name for group in obj.groups.all()])
        return ''

    def get_export_headers(self):
        return super().get_export_headers() + ['file_count', 'file_name', 'file_format', 'file_size_bytes']

    def _build_first_row(self, obj, file=None, file_count=''):
        """Build one export row for obj, with optional file columns appended."""
        row = [self.export_field(f, obj) for f in self.get_export_fields()]
        if file is not None:
            name = file.name or os.path.basename(file.file.name)
            format = os.path.splitext(file.file.name)[1].lstrip('.').upper()
            try:
                size = file.file.size
            except (FileNotFoundError, OSError):
                size = ''
            row += [file_count, name, format, size]
        else:
            row += [file_count, '', '', '']
        return row

    def export(self, queryset=None, *args, **kwargs):
        import tablib
        if queryset is None:
            queryset = self.get_queryset()
        dataset = tablib.Dataset(headers=self.get_export_headers())
        qs = queryset.prefetch_related('files', 'groups', 'status', 'license')
        empty_resource_cols = [''] * (len(self.get_export_fields()) + 1)  # +1 for file_count
        for obj in qs:
            files = list(obj.files.all())
            if files:
                dataset.append(self._build_first_row(obj, files[0], file_count=str(len(files))))
                for f in files[1:]:
                    name = f.name or os.path.basename(f.file.name)
                    format = os.path.splitext(f.file.name)[1].lstrip('.').upper()
                    try:
                        size = f.file.size
                    except (FileNotFoundError, OSError):
                        size = ''
                    dataset.append(empty_resource_cols + [name, format, size])
            else:
                dataset.append(self._build_first_row(obj))
        return dataset


@admin.register(models.Resource)
class Resource(ExportActionModelAdmin):
    list_display = ['archived', 'name', 'kind']
    list_display_links = ['name']
    list_filter = ['site', 'archived', 'kind', 'groups', 'license']
    filter_horizontal = ['groups']
    search_fields = ['name', 'description']
    resource_classes = [ResourceResource]
    inlines = [ContributorInline, ResourceFileInline]
    form = forms.ResourceAdminForm


@admin.register(models.StudyDesignCollection)
class StudyDesignCollection(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'site']
    list_display_links = ['name']
    list_filter = ['site']


@admin.register(models.StudyDesign)
class StudyDesign(admin.ModelAdmin):
    list_display = ['archived', 'name']
    list_display_links = ['name']
    list_filter = ['site', 'archived', 'groups', 'license']
    filter_horizontal = ['groups']
    search_fields = ['name', 'description']
    inlines = [ContributorInline]
    form = forms.StudyDesignAdminForm


@admin.register(models.StudyDesignNodeType)
class StudyDesignNodeType(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'name', 'color']
    list_display_links = ['name']
    list_filter = ['site']


@admin.register(models.StudyDesignNodeTag)
class StudyDesignNodeFlag(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    list_filter = ['site']


@admin.register(models.StudyDesignNode)
class StudyDesignNode(admin.ModelAdmin):
    list_display = ['id', 'name', 'study_design']
    list_display_links = ['id']
    list_filter = ['study_design', 'organisation']
    filter_horizontal = ['resources', 'tags']
    search_fields = ['name', 'description', 'resources__name', 'resources__description']


@admin.register(models.StudyDesignEdge)
class StudyDesignEdge(admin.ModelAdmin):
    list_display = ['id', 'source', 'source__id', 'target', 'target__id']
    list_display_links = ['id']
    list_filter = ['study_design']
    search_fields = ['source__name', 'target__name']
