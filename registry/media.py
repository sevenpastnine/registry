from pathlib import Path

from django.conf import settings
from django.views.static import serve
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework import authentication


def x_accel_redirect(request, path):
    if settings.DEBUG:
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    else:
        response = HttpResponse()
        response['Content-Type'] = ''
        response['X-Accel-Redirect'] = Path('/protected-media/', path).as_posix()
        return response


def check_access(request, path):
    if request.user.is_authenticated:
        return x_accel_redirect(request, path)
    else:
        try:
            if not authentication.TokenAuthentication().authenticate(request):
                return HttpResponseForbidden()
            else:
                return x_accel_redirect(request, path)
        except Exception:
            return HttpResponseForbidden()
