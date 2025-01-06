import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

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


@csrf_exempt
@require_POST
# TODO Implement token based authentication/authorization
def study_design_map(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception as e:
        raise ValueError(f'Invalid YDoc document: {e}')

    study_design = get_object_or_404(models.StudyDesign, pk=data['payload']['documentName'])

    # TODO Implement signature verification
    # print(request.headers)
    # 'X-Hocuspocus-Signature-256': 'sha256=8e8e78eade79acfa79a6cba8d6c5b899c83827c9dc5de2a4169710ebc3a93db1'

    match data.get('event'):
        case 'create':
            # Load from DB
            return JsonResponse(study_design.to_ydoc())
        case 'change':
            # Save to DB
            study_design.update_from_ydoc(data['payload']['document'])
            return JsonResponse({})
        case _:
            raise ValueError(f'Unknown YDoc event: {data.get("event")}')
