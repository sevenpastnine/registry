from typing import Union, Dict

from django.conf import settings
from django.http import HttpRequest
from django.contrib.sites.models import Site
from django.contrib.sites.requests import RequestSite
from django.contrib.sites.shortcuts import get_current_site as get_current_site_django


def get_current_site(request_or_scope: Union[HttpRequest, Dict]) -> Union[Site, RequestSite]:
    """
    Retrieves the current site based on the provided request or scope.

    Args:
        request_or_scope (Union[HttpRequest, dict]): The request object or a dictionary containing scope information.

    Returns:
        Site: The current site object.

    Raises:
        Site.DoesNotExist: If no Site object is found with the given criteria.

    Notes:
        - If `request_or_scope` is a dictionary, it is assumed to be an wesocket scope.
        - If the `SITE_ID` setting is defined, the site with that ID is returned.
        - Otherwise, the site is determined based on the domain in the scope.
        - If `request_or_scope` is not a dictionary, it is assumed to be a Django HttpRequest object and the function `get_current_site_django` is called.
    """
    if isinstance(request_or_scope, dict):
        scope = request_or_scope
        if hasattr(settings, 'SITE_ID'):
            return Site.objects.get(id=settings.SITE_ID)
        else:
            return Site.objects.get(domain=dict(scope['headers'])[b'host'].decode('utf-8'))
    else:
        return get_current_site_django(request_or_scope)
