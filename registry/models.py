import os
import shortuuid

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from django_countries.fields import CountryField

UUID_LENGTH = 12


def uuid():
    su = shortuuid.ShortUUID(alphabet='23456789abcdefghjklmnpqrstuvwxyz')
    return su.random(length=UUID_LENGTH)


class BaseModel(models.Model):
    id = models.CharField(primary_key=True, max_length=22, default=uuid, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Person(BaseModel):
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


class PersonRole(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Organisation(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=50, unique=True)
    country = CountryField()
    ror = models.CharField('ROR Id', max_length=9, null=True, blank=True)
    people = models.ManyToManyField(Person, blank=True, related_name='organisations')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Group(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    people = models.ManyToManyField(Person, blank=True, related_name='groups')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class License(BaseModel):
    name = models.CharField(max_length=255)
    url = models.URLField('URL')
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.description}'


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


class ResourceStatus(BaseModel):
    position = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['position']
        verbose_name_plural = 'Resource statuses'

    def __str__(self):
        return self.name


class Resource(BaseModel):

    class Kind(models.TextChoices):
        MATERIAL = 'MATERIAL', 'Material'
        TEST_METHOD = 'TEST_METHOD', 'Test method'
        PROTOCOL_SOP = 'PROTOCOL_SOP', 'Protocol or SOP'
        DATA = 'DATA', 'Data'

    archived = models.BooleanField(default=False, help_text='If checked, this resource will not be shown in the registry by default. It will still be accessible if requested.')

    name = models.CharField(max_length=255)
    kind = models.CharField('Type of resource', max_length=100, choices=Kind.choices)
    description = models.TextField(null=True, blank=True)

    status = models.ForeignKey(ResourceStatus, on_delete=models.PROTECT, related_name='resources')
    license = models.ForeignKey(License, on_delete=models.PROTECT, null=True, blank=True, related_name='resources')
    groups = models.ManyToManyField(Group, blank=True, related_name='resources', verbose_name='Use cases')
    contributors = GenericRelation(Contributor)

    data_link = models.URLField('Resource link', null=True, blank=True, help_text='Link to the resource (e.g. Zenodo, Figshare, etc.)')
    data_file = models.FileField('Resource file', upload_to='resources/', null=True, blank=True, help_text='File containing data or information on the resource. In case of multiple files, please upload a zip file.')

    harmonised_json = models.JSONField('Harmonised JSON data', null=True, blank=True, help_text='JSON file containing the harmonised data')

    class Meta:
        ordering = ['name', 'kind']

    def __str__(self):
        return self.name

    @property
    def data_file_name(self):
        return os.path.basename(self.data_file.name)


def resource_file_path(instance, filename):
    return f'resources/files/{instance.resource.id}/{filename}'


class ResourceFile(BaseModel):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to=resource_file_path, help_text='File containing data or information on the resource')

    class Meta:
        ordering = ['resource', 'file']

    def __str__(self):
        return os.path.basename(self.file.name)


class ResourceCollection(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    groups = models.ManyToManyField(Group, blank=True, related_name='resource_collections', verbose_name='Use cases')

    resources = models.ManyToManyField(Resource, blank=True, related_name='collections')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StudyDesign(BaseModel):
    archived = models.BooleanField(default=False, help_text='If checked, this study design will not be shown in the registry by default. It will still be accessible if requested.')

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    license = models.ForeignKey(License, on_delete=models.PROTECT, null=True, blank=True, related_name='study_designs')
    groups = models.ManyToManyField(Group, blank=True, related_name='study_designs', verbose_name='Use cases')
    contributors = GenericRelation(Contributor)

    instance_map_link = models.URLField('Instance map link', null=True, blank=True, help_text='Link to the Instance map')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
