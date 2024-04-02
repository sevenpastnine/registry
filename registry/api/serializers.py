from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType

from .. import models


class PersonRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersonRole
        fields = ['id', 'name']


class PersonSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = models.Person
        fields = ['id', 'name', 'email', 'orcid']

    def get_name(self, obj):
        return obj.user.get_full_name() if obj.user.get_full_name() else obj.user.username

    def get_email(self, obj):
        return str(obj.user.email)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ['id', 'name', 'description', 'people']


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.License
        fields = ['id', 'name', 'url', 'description']


class ResourceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResourceStatus
        fields = ['id', 'name']


class ResourceKindSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            'id': obj.name,
            'name': obj.label,
        }


class TaggedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contributor
        fields = [
            'person',
            'role',
        ]


class ResourceSerializer(serializers.ModelSerializer):
    contributors = TaggedItemSerializer(many=True)

    class Meta:
        model = models.Resource
        fields = ['id', 'archived', 'name', 'kind', 'description', 'status', 'license', 'groups', 'contributors', 'data_link', 'harmonised_json']

    def validate_contributors(self, data):
        if not len(data):
            raise serializers.ValidationError('At least one contributor is required.')
        return super().validate(data)

    def create(self, validated_data):
        groups = validated_data.pop('groups', [])
        contributors = validated_data.pop('contributors', [])
        resource = models.Resource.objects.create(**validated_data)

        resource.groups.set(groups)

        content_type = ContentType.objects.get_for_model(resource.__class__)
        [models.Contributor.objects.create(
            person=contributor['person'],
            role=contributor['role'],
            content_type=content_type,
            object_id=resource.id)
            for contributor in contributors]

        return resource

    def update(self, resource, validated_data):
        groups = validated_data.pop('groups', None)
        contributors = validated_data.pop('contributors', None)
        super().update(resource, validated_data)

        if groups is not None:
            resource.groups.set(groups)

        if contributors is not None:
            content_type = ContentType.objects.get_for_model(resource.__class__)
            resource.contributors.all().delete()
            [models.Contributor.objects.create(
                person=contributor['person'],
                role=contributor['role'],
                content_type=content_type,
                object_id=resource.id)
                for contributor in contributors]

        return resource


class ResourceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResourceFile
        fields = ['id', 'resource', 'name', 'file']


class ResourceCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ResourceCollection
        fields = ['id', 'name', 'description', 'groups', 'resources']
