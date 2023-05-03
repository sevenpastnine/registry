from rest_framework import serializers

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
            # 'id',
            'person',
            'role',
        ]


class ResourceSerializer(serializers.ModelSerializer):
    contributors = TaggedItemSerializer(many=True, read_only=True)

    class Meta:
        model = models.Resource
        fields = ['pk', 'archived', 'name', 'kind', 'description', 'status', 'license', 'groups', 'data_link', 'data_file', 'contributors']
