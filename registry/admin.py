from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from adminsortable2.admin import SortableAdminMixin

from . import models


@admin.register(models.Person)
class Person(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'orcid', 'email']
    list_display_links = ['email']
    list_filter = ['organisations', 'groups']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']


@admin.register(models.PersonRole)
class PersonRole(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']


@admin.register(models.Organisation)
class Organisation(admin.ModelAdmin):
    list_display = ['ror', 'short_name', 'name']
    list_display_links = ['name']
    filter_horizontal = ['people']


@admin.register(models.Group)
class Group(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    filter_horizontal = ['people']


@admin.register(models.License)
class License(admin.ModelAdmin):
    list_display = ['name', 'url']
    list_display_links = ['name']


@admin.register(models.ResourceStatus)
class ResourceStatus(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']


class ContributorInline(GenericTabularInline):
    model = models.Contributor
    extra = 0


class ResourceFileInline(admin.TabularInline):
    model = models.ResourceFile
    extra = 0


@admin.register(models.Resource)
class Resource(admin.ModelAdmin):
    list_display = ['archived', 'name', 'kind']
    list_display_links = ['name']
    list_filter = ['archived', 'kind', 'groups', 'license']
    filter_horizontal = ['groups']
    search_fields = ['name', 'description']
    inlines = [ContributorInline, ResourceFileInline]


@admin.register(models.ResourceCollection)
class ResourceCollection(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    list_filter = ['groups']
    filter_horizontal = ['groups', 'resources']
    search_fields = ['name', 'description', 'resources__name', 'resources__description']


@admin.register(models.StudyDesign)
class StudyDesign(admin.ModelAdmin):
    list_display = ['archived', 'name']
    list_display_links = ['name']
    list_filter = ['archived', 'groups', 'license']
    filter_horizontal = ['groups']
    search_fields = ['name', 'description']
    inlines = [ContributorInline]
