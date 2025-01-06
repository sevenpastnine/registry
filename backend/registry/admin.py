from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from adminsortable2.admin import SortableAdminMixin

from . import models
from . import admin_forms as forms


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
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    filter_horizontal = ['sites']


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


@admin.register(models.Resource)
class Resource(admin.ModelAdmin):
    list_display = ['archived', 'name', 'kind']
    list_display_links = ['name']
    list_filter = ['site', 'archived', 'kind', 'groups', 'license']
    filter_horizontal = ['groups']
    search_fields = ['name', 'description']
    inlines = [ContributorInline, ResourceFileInline]
    form = forms.ResourceAdminForm


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
