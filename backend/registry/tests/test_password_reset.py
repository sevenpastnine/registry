from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.urls import reverse

from backend.registry.models import Person, Project


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class CustomPasswordResetViewTests(TestCase):
    """Tests for the CustomPasswordResetView override."""

    def setUp(self):
        self.site = Site.objects.get_current()
        self.project = Project.objects.create(site=self.site, slug='test-reset')

        self.inactive_user = User.objects.create_user(
            username='inactive@example.com',
            email='inactive@example.com',
        )
        self.inactive_user.set_unusable_password()
        self.inactive_user.save()
        self.inactive_person = Person.objects.create(user=self.inactive_user)
        self.inactive_person.sites.add(self.site)

        self.active_user = User.objects.create_user(
            username='active@example.com',
            email='active@example.com',
            password='testpass123',
        )
        self.active_person = Person.objects.create(user=self.active_user)
        self.active_person.sites.add(self.site)

        self.suspended_user = User.objects.create_user(
            username='suspended@example.com',
            email='suspended@example.com',
            is_active=False,
        )
        self.suspended_user.set_unusable_password()
        self.suspended_user.save()
        self.suspended_person = Person.objects.create(user=self.suspended_user)
        self.suspended_person.sites.add(self.site)

    # Inactive user gets neutral response and activation email

    def test_inactive_email_redirects_to_done_and_sends_activation_email(self):
        """Pending user gets neutral reset response and receives activation instructions."""
        response = self.client.post(
            reverse('password_reset'), {'email': 'inactive@example.com'}
        )
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['inactive@example.com'])
        self.assertIn('/accounts/activate/', mail.outbox[0].body)

    # Active user gets the standard reset email with cross-site note

    def test_active_email_sends_reset_email_with_cross_site_note(self):
        """Active user gets the standard Django reset email, which mentions cross-site credentials."""
        response = self.client.post(
            reverse('password_reset'), {'email': 'active@example.com'}
        )
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['active@example.com'])
        # The reset email should remind users their password works across all registries
        self.assertIn('all Registries', mail.outbox[0].body)

    # Suspended user gets neutral response

    def test_suspended_email_does_not_redirect_to_activate(self):
        """Suspended user (is_active=False) is not redirected to activation — no email sent."""
        response = self.client.post(
            reverse('password_reset'), {'email': 'suspended@example.com'}
        )
        # Falls through to Django's standard reset flow, which silently skips inactive users
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 0)
