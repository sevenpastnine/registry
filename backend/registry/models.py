import os
import shortuuid

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site as Site
from django.contrib.sites.managers import CurrentSiteManager

from django_countries.fields import CountryField

UUID_LENGTH = 12


# -----------------------------------------------------------------------------
# Utils

def uuid():
    # Keep the alphabet and length in sync with the one on the frontend (studyDesignMaps/shortUUID.ts)
    su = shortuuid.ShortUUID(alphabet='23456789abcdefghjklmnpqrstuvwxyz')
    return su.random(length=UUID_LENGTH)


class BaseModel(models.Model):
    id = models.CharField(primary_key=True, max_length=UUID_LENGTH, default=uuid, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# -----------------------------------------------------------------------------
# Project

class Project(BaseModel):
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(null=True, blank=True, upload_to='projects/logos')
    style = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['site__name']

    def __str__(self):
        return str(self.site)

    @property
    def domain(self):
        return self.site.domain

    @property
    def name(self):
        return self.site.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self._state.adding:
            for (pos, type) in enumerate(settings.REGISTRY_DEFAULT_NODE_TYPES):
                StudyDesignNodeType.objects.create(
                    site=self.site,
                    name=type['name'],
                    color=type['color'],
                    description=type.get('description', ''),
                    position=pos
                )


class SiteMixin(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    objects = models.Manager()
    site_objects = CurrentSiteManager('site')

    class Meta:
        abstract = True


class SitesMixin(models.Model):
    sites = models.ManyToManyField(Site)
    objects = models.Manager()
    site_objects = CurrentSiteManager('sites')

    class Meta:
        abstract = True


# -----------------------------------------------------------------------------
# Licenses

class License(BaseModel, SitesMixin):
    name = models.CharField(max_length=255)
    url = models.URLField('URL', null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.description:
            return f'{self.name} - {self.description}'
        else:
            return self.name


# -----------------------------------------------------------------------------
# People and groups

class Person(BaseModel, SitesMixin):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    orcid = models.CharField('ORCID Id', max_length=19, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'People'
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return self.full_name

    @property
    def email(self):
        return self.user.email

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def full_name(self):
        return self.user.get_full_name() if self.user.get_full_name() else self.user.username

    @property
    def orcid_url(self):
        if self.orcid is not None:
            return f'https://orcid.org/{self.orcid}'
        else:
            return None


class PersonRole(BaseModel, SiteMixin):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']
        unique_together = ['site', 'name']

    def __str__(self):
        return self.name


class Organisation(BaseModel, SitesMixin):
    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    country = CountryField()
    ror = models.CharField('ROR Id', max_length=9, null=True, blank=True)
    people = models.ManyToManyField(Person, blank=True, related_name='organisations')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Group(BaseModel, SiteMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    people = models.ManyToManyField(Person, blank=True, related_name='groups')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Contributor(BaseModel):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='contributes_to_resources')
    role = models.ForeignKey(PersonRole, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=UUID_LENGTH)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ['content_type', 'object_id', 'person', 'role']
        ordering = ['role__name', 'person']
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return f'{self.role.name} - {self.person.full_name}'


# -----------------------------------------------------------------------------
# Resources

class ResourceStatus(BaseModel, SiteMixin):
    position = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['position']
        verbose_name_plural = 'Resource statuses'
        unique_together = ['site', 'name']

    def __str__(self):
        return self.name


class Resource(BaseModel, SiteMixin):

    class Kind(models.TextChoices):
        MATERIAL = 'MATERIAL', 'Material'
        TEST_METHOD = 'TEST_METHOD', 'Test method'
        PROTOCOL_SOP = 'PROTOCOL_SOP', 'Protocol or SOP'
        DATA = 'DATA', 'Data'

    archived = models.BooleanField(
        default=False,
        help_text='If checked, this resource will not be shown in the registry by default. It will still be accessible if requested.'
    )

    name = models.CharField(max_length=255)
    kind = models.CharField('Type of resource', max_length=100, choices=Kind.choices)
    description = models.TextField(null=True, blank=True)

    status = models.ForeignKey(ResourceStatus, on_delete=models.PROTECT, related_name='resources')
    license = models.ForeignKey(License, on_delete=models.PROTECT, null=True, blank=True, related_name='resources')
    groups = models.ManyToManyField(Group, blank=True, related_name='resources', verbose_name='Use cases')
    contributors = GenericRelation(Contributor)

    data_link = models.URLField('Resource link', null=True, blank=True,
                                help_text='Link to the resource (e.g. Zenodo, Figshare, etc.)')

    harmonised_json = models.JSONField('Harmonised JSON data', null=True, blank=True,
                                       help_text='JSON file containing the harmonised data')

    class Meta:
        ordering = ['name', 'kind']

    def __str__(self):
        return self.name

    @property
    def organisations(self):
        return Organisation.objects.filter(
            people__contributes_to_resources__object_id=self.id,
            people__contributes_to_resources__content_type=ContentType.objects.get_for_model(Resource)
        ).distinct()

    def to_ydoc(self):
        return {
            'id': self.id,
            'name': self.name,
        }


def resource_file_path(instance, filename):
    return f'{settings.REGISTRY_RESOURCE_FILE_DIR}{instance.resource.id}/{filename}'


class ResourceFile(BaseModel):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='files')

    name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=resource_file_path)

    class Meta:
        ordering = ['resource', 'file']

    def __str__(self):
        return os.path.basename(self.file.name)


# -----------------------------------------------------------------------------
# Study designs

class StudyDesign(BaseModel, SiteMixin):
    archived = models.BooleanField(
        default=False,
        help_text='If checked, this study design map will not be shown in the registry by default. It will still be accessible if requested.'
    )

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    license = models.ForeignKey(License, on_delete=models.PROTECT, null=True, blank=True, related_name='study_designs')
    groups = models.ManyToManyField(Group, blank=True, related_name='study_designs', verbose_name='Use cases')
    contributors = GenericRelation(Contributor)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_ydoc(self):
        return {
            'nodes': dict([(node.id, node.to_ydoc()) for node in self.nodes.all()]),   # type: ignore
            'edges': dict([(edge.id, edge.to_ydoc()) for edge in self.edges.all()])    # type: ignore
        }

    def update_from_ydoc(self, ydoc):
        nodes_db = dict([(node.id, node) for node in self.nodes.all()])  # type: ignore
        nodes_db_set = set(nodes_db.keys())
        nodes_ydoc = ydoc.get('nodes', {})
        nodes_ydoc_set = set([node_id for node_id in nodes_ydoc.keys()])

        edges_db = dict([(edge.id, edge) for edge in self.edges.all()])  # type: ignore
        edges_db_set = set(edges_db.keys())
        edges_ydoc = ydoc.get('edges', {})
        edges_ydoc_set = set([edge_id for edge_id in edges_ydoc.keys()])

        # Delete edges and nodes that are not in the ydoc

        for edge_id in edges_db_set - edges_ydoc_set:
            edges_db[edge_id].delete()

        for node_id in nodes_db_set - nodes_ydoc_set:
            nodes_db[node_id].delete()

        def get_organisation(node_ydoc):
            if node_ydoc['data'].get('organisation'):
                if not Organisation.objects.filter(id=node_ydoc['data']['organisation']).exists():
                    return None
                else:
                    return Organisation.objects.get(id=node_ydoc['data']['organisation'])
            else:
                return None

        # Create nodes and edges that are not in the db

        for node_id in nodes_ydoc_set - nodes_db_set:
            node_ydoc = nodes_ydoc[node_id]

            node = StudyDesignNode.objects.create(
                id=node_id,
                study_design=self,

                type=StudyDesignNodeType.site_objects.get(id=node_ydoc['type']),
                position_x=node_ydoc['position']['x'],
                position_y=node_ydoc['position']['y'],

                name=node_ydoc['data']['name'],
                description=node_ydoc['data'].get('description'),
                organisation=get_organisation(node_ydoc),
            )

            node.resources.set(Resource.objects.filter(id__in=[resource['id'] for resource in node_ydoc['data']['resources']]))

        for edge_id in edges_ydoc_set - edges_db_set:
            StudyDesignEdge.objects.create(
                id=edge_id,
                study_design=self,
                source_id=edges_ydoc[edge_id]['source'],
                sourceHandle=edges_ydoc[edge_id]['sourceHandle'],
                target_id=edges_ydoc[edge_id]['target'],
                targetHandle=edges_ydoc[edge_id]['targetHandle']
            )

        # Update nodes and edges that are both in ydoc and in db

        for node_id in nodes_ydoc_set & nodes_db_set:
            node_db = nodes_db[node_id]
            node_ydoc = nodes_ydoc[node_id]

            node_db.type = StudyDesignNodeType.site_objects.get(id=node_ydoc['type'])
            node_db.position_x = node_ydoc['position']['x']
            node_db.position_y = node_ydoc['position']['y']

            node_db.name = node_ydoc['data']['name']
            node_db.description = node_ydoc['data'].get('description')
            node_db.organisation = get_organisation(node_ydoc)

            node_db.save()

            node_db.resources.set(Resource.objects.filter(id__in=[resource['id'] for resource in node_ydoc['data']['resources']]))

        for edge_id in edges_ydoc_set & edges_db_set:
            edge_db = edges_db[edge_id]
            edge_db.source_id = edges_ydoc[edge_id]['source']
            edge_db.sourceHandle = edges_ydoc[edge_id]['sourceHandle']
            edge_db.target_id = edges_ydoc[edge_id]['target']
            edge_db.targetHandle = edges_ydoc[edge_id]['targetHandle']
            edge_db.save()


class StudyDesignNodeType(BaseModel, SiteMixin):
    name = models.CharField(max_length=20)
    color = models.CharField(max_length=7)
    description = models.TextField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.name


class StudyDesignNodeTag(BaseModel, SiteMixin):
    name = models.CharField(max_length=25, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StudyDesignNode(BaseModel):
    study_design = models.ForeignKey(StudyDesign, on_delete=models.CASCADE, related_name='nodes')

    type = models.ForeignKey(StudyDesignNodeType, on_delete=models.PROTECT, related_name='nodes')
    position_x = models.IntegerField()
    position_y = models.IntegerField()

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT, null=True, blank=True, related_name='study_design_nodes')
    related_study_design = models.ForeignKey(StudyDesign, on_delete=models.PROTECT, null=True, blank=True, related_name='related_nodes')
    resources = models.ManyToManyField(Resource, blank=True, related_name='study_design_nodes')
    tags = models.ManyToManyField(StudyDesignNodeTag, blank=True, related_name='nodes')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def non_archived_resources(self):
        return self.resources.filter(archived=False)

    def to_ydoc(self):
        return {
            'id': self.id,
            'type': self.type.id,
            'position': {
                'x': self.position_x,
                'y': self.position_y
            },
            'data': {
                'name': self.name,
                'description': self.description,
                'organisation': self.organisation.id if self.organisation else None,
                'resources': [resource.to_ydoc() for resource in self.resources.all()],
            }
        }


class StudyDesignEdge(BaseModel):
    study_design = models.ForeignKey(StudyDesign, on_delete=models.CASCADE, related_name='edges')

    source = models.ForeignKey(StudyDesignNode, on_delete=models.CASCADE, related_name='edges_out')
    sourceHandle = models.CharField(max_length=100)
    target = models.ForeignKey(StudyDesignNode, on_delete=models.CASCADE, related_name='edges_in')
    targetHandle = models.CharField(max_length=100)

    class Meta:
        unique_together = ['source', 'target']

    def __str__(self):
        return f'{self.source.name} - {self.target.name}'

    def to_ydoc(self):
        return {
            'id': self.id,
            'source': self.source.id,
            'sourceHandle': self.sourceHandle,
            'target': self.target.id,
            'targetHandle': self.targetHandle
        }
