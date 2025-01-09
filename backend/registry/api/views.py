
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, mixins, authentication, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .. import models
from . import serializers


@login_required
def docs(request):
    return render(request, 'registry/api/docs.html', {
        'hostname': request.get_host(),
        'scheme': 'https' if request.is_secure() else 'http',
        'token': Token.objects.get_or_create(user=request.user)[0].key if request.user.is_authenticated else None,
    })


class AuthzMixin:
    authentication_classes = [authentication.SessionAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class ListRetrieveViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    pass


class PersonRoleViewSet(AuthzMixin, ListRetrieveViewSet):
    queryset = models.PersonRole.objects.all()
    serializer_class = serializers.PersonRoleSerializer


class PersonViewSet(AuthzMixin, ListRetrieveViewSet):
    queryset = models.Person.objects.all()
    serializer_class = serializers.PersonSerializer


class GroupViewSet(AuthzMixin, ListRetrieveViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer


class LicenseViewSet(AuthzMixin, ListRetrieveViewSet):
    queryset = models.License.objects.all()
    serializer_class = serializers.LicenseSerializer


class ResourceKindViewSet(AuthzMixin, viewsets.ViewSet):
    def list(self, request):
        queryset = models.Resource.Kind
        serializer = serializers.ResourceKindSerializer(queryset, many=True)
        return Response(serializer.data)


class ResourceStatusViewSet(AuthzMixin, ListRetrieveViewSet):
    queryset = models.ResourceStatus.objects.all()
    serializer_class = serializers.ResourceStatusSerializer


class ResourceViewSet(AuthzMixin, viewsets.ModelViewSet):
    queryset = models.Resource.objects.filter(archived=False)
    serializer_class = serializers.ResourceSerializer
    http_method_names = ['head', 'options', 'get', 'post', 'patch']


class ResourceFileViewSet(AuthzMixin, viewsets.ModelViewSet):
    queryset = models.ResourceFile.objects.filter(resource__archived=False)
    serializer_class = serializers.ResourceFileSerializer
    http_method_names = ['head', 'options', 'get', 'post', 'patch']
