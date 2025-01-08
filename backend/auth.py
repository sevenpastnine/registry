import asyncio
from functools import wraps
from typing import Optional, Callable
from asgiref.sync import sync_to_async

from django.http import HttpRequest
from django.http import HttpResponseForbidden
from django.contrib.sites.shortcuts import get_current_site


def site_member_required(view_func: Optional[Callable] = None):
    async def check_membership(request: HttpRequest) -> bool:
        if not hasattr(request.user, 'person'):
            return False

        current_site = await sync_to_async(get_current_site)(request)
        return await sync_to_async(
            lambda: request.user.person.sites.filter(id=current_site.id).exists()  # type: ignore
        )()

    def sync_check_membership(request: HttpRequest) -> bool:
        if not hasattr(request.user, 'person'):
            return False

        current_site = get_current_site(request)
        return request.user.person.sites.filter(id=current_site.id).exists()  # type: ignore

    # If used as a regular function
    if view_func is None:
        return sync_check_membership

    # If used as a decorator
    @wraps(view_func)
    async def async_wrapper(request, *args, **kwargs):
        if not await check_membership(request):
            return HttpResponseForbidden('Access denied')

        if asyncio.iscoroutinefunction(view_func):
            return await view_func(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)

    @wraps(view_func)
    def sync_wrapper(request, *args, **kwargs):
        if not sync_check_membership(request):
            return HttpResponseForbidden('Access denied')
        return view_func(request, *args, **kwargs)

    if asyncio.iscoroutinefunction(view_func):
        return async_wrapper

    return sync_wrapper
