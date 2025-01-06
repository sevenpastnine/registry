from pathlib import Path

from django.conf import settings
from django.views.static import serve
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework import authentication

from . import models


def x_accel_redirect(request, path):
    if settings.DEBUG:
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    else:
        response = HttpResponse()
        response['Content-Type'] = ''
        response['X-Accel-Redirect'] = Path('/protected-media/', path).as_posix()
        return response


def check_access(request, path):
    site = request.site
    user = request.user

    if user.is_authenticated:
        if not hasattr(user, 'person') or site not in user.person.sites.all():
            return HttpResponseForbidden()
        elif path.startswith(settings.REGISTRY_RESOURCE_FILE_DIR) and not models.ResourceFile.objects.filter(file=path, resource__site=site).exists():
            return HttpResponseForbidden()
        else:
            return x_accel_redirect(request, path)
    else:
        try:
            if not authentication.TokenAuthentication().authenticate(request):
                return HttpResponseForbidden()
            else:
                return x_accel_redirect(request, path)
        except Exception:
            return HttpResponseForbidden()
