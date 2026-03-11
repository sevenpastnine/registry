import asyncio
from functools import wraps
from typing import Optional, Callable
from asgiref.sync import sync_to_async

from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView
from django.contrib.sites.models import Site
from django.core import signing
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from backend.registry.models import Person
from backend.utils import normalize_email


def _get_current_db_site(request: HttpRequest) -> Site:
    """Return the current site as a guaranteed database-backed Site instance."""
    return Site.objects.get_current(request)


def site_member_required(view_func: Optional[Callable] = None):
    async def check_membership(request: HttpRequest) -> bool:
        if not hasattr(request.user, 'person'):
            return False

        current_site = await sync_to_async(_get_current_db_site)(request)
        return await sync_to_async(
            lambda: request.user.person.sites.filter(id=current_site.id).exists()  # type: ignore
        )()

    def sync_check_membership(request: HttpRequest) -> bool:
        if not hasattr(request.user, 'person'):
            return False

        current_site = _get_current_db_site(request)
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


_ACTIVATION_SALT = 'user-activation'
_ACTIVATION_MAX_AGE = 259200  # 3 days in seconds


def _send_activation_email(request: HttpRequest, user: User, site: Site) -> None:
    """Send a signed activation link to an inactive user."""
    token = signing.dumps({'user_id': user.pk, 'site_id': site.pk}, salt=_ACTIVATION_SALT)
    context = {
        'user': user,
        'site': site,
        'confirm_url': request.build_absolute_uri(
            reverse('activation_confirm', kwargs={'token': token})
        ),
        'support_email': settings.REGISTRY_SUPPORT_EMAIL,
    }
    subject = render_to_string('registration/activation_email_subject.txt', context).strip()
    body = render_to_string('registration/activation_email.txt', context)
    send_mail(subject, body, settings.REGISTRY_SUPPORT_EMAIL_WITH_NAME, [user.email])


def _send_existing_user_email(request: HttpRequest, user: User, site: Site) -> None:
    """Send a 'you already have an account' notice to an active user."""
    context = {
        'user': user,
        'site': site,
        'login_url': request.build_absolute_uri(reverse('login')),
        'password_reset_url': request.build_absolute_uri(reverse('password_reset')),
        'support_email': settings.REGISTRY_SUPPORT_EMAIL,
    }
    subject = render_to_string('registration/activation_existing_email_subject.txt', context).strip()
    body = render_to_string('registration/activation_existing_email.txt', context)
    send_mail(subject, body, settings.REGISTRY_SUPPORT_EMAIL_WITH_NAME, [user.email])


def activation_request(request: HttpRequest) -> HttpResponse:
    """
    Handle GET and POST for the activation request form.

    GET: render the form, optionally pre-filling email from ?email=.
    POST: look up the email and send a targeted email based on account state.
    Always redirects to activate_done with a neutral on-site message to avoid
    leaking information about whether a given email is registered.
    """
    if request.method == 'POST':
        email = normalize_email(request.POST.get('email', ''))
        if not email:
            return redirect(reverse('activation_done'))

        current_site = _get_current_db_site(request)

        try:
            person = Person.objects.get(user__username=email, sites=current_site)
            user = person.user
            if not user.is_active:
                pass  # Suspended account — treat as unknown; do not reveal status.
            elif user.has_usable_password():
                _send_existing_user_email(request, user, current_site)
            else:
                _send_activation_email(request, user, current_site)
        except Person.DoesNotExist:
            pass  # Always show the same neutral message; do not reveal activation status.

        return redirect(reverse('activation_done'))

    email = request.GET.get('email', '')
    return render(request, 'registration/activation.html', {'email': email})


def _resolve_activation_user(token: str, site: Site) -> Optional[User]:
    """
    Validate an activation token and return the User only if the token
    signature is valid, not expired, the site matches, and the user is still
    pending activation.
    """
    try:
        payload = signing.loads(token, salt=_ACTIVATION_SALT, max_age=_ACTIVATION_MAX_AGE)
        user_pk = payload.get('user_id')
        token_site_id = payload.get('site_id')
        if token_site_id != site.pk:
            return None

        user = User.objects.get(pk=user_pk)
        if not user.is_active or user.has_usable_password():
            return None

        return user if Person.objects.filter(user=user, sites=site).exists() else None
    except (signing.BadSignature, signing.SignatureExpired, User.DoesNotExist, AttributeError):
        return None


def activation_confirm(request: HttpRequest, token: str) -> HttpResponse:
    """
    Handle GET and POST for the activation confirmation step.

    GET: show the set-password form if the token is valid and the user is inactive.
    POST: set the user's password and activate the account.
    """
    current_site = _get_current_db_site(request)
    user = _resolve_activation_user(token, current_site)
    if user is None:
        return render(request, 'registration/activation_confirm.html', {'valid_token': False})

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('activation_complete'))
    else:
        form = SetPasswordForm(user)

    return render(request, 'registration/activation_confirm.html', {
        'form': form,
        'token': token,
        'valid_token': True,
    })


def activation_done(request: HttpRequest) -> HttpResponse:
    """Render the neutral post-request page shown after any activation form submission."""
    return render(request, 'registration/activation_done.html')


def activation_complete(request: HttpRequest) -> HttpResponse:
    """Render the success page shown after a user has set their password and activated their account."""
    return render(request, 'registration/activation_complete.html')


class PasswordResetView(DjangoPasswordResetView):
    """
    Custom password reset view that:
    - Redirects inactive users to the activation flow instead of sending a reset email.
    - Adds the registry support email and a cross-site credentials note to the reset email context.
    """

    extra_email_context = {
        'registry_support_email': settings.REGISTRY_SUPPORT_EMAIL,
    }

    def form_valid(self, form):
        email = form.cleaned_data['email']
        current_site = _get_current_db_site(self.request)

        try:
            person = Person.objects.get(user__username=email, sites=current_site)
            if person.user.is_active and not person.user.has_usable_password():
                _send_activation_email(self.request, person.user, current_site)
                return redirect(reverse('password_reset_done'))
        except Person.DoesNotExist:
            pass

        return super().form_valid(form)
