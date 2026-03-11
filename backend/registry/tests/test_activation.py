from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail, signing
from django.urls import reverse

from backend.registry.models import Person, Project


def _make_token(user: User, site: Site) -> str:
    """Generate a valid activation token for the given user."""
    return signing.dumps({'user_id': user.pk, 'site_id': site.pk}, salt='user-activation')


class ActivationRequestViewSetup(TestCase):
    """Shared setUp for ActivationRequestView and ActivationConfirmView tests."""

    def setUp(self):
        self.site = Site.objects.get_current()
        self.project = Project.objects.create(site=self.site, slug='test-reg')

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


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ActivationRequestViewTests(ActivationRequestViewSetup):
    """Tests for activation_request (GET and POST)."""

    # GET

    def test_get_renders_form(self):
        response = self.client.get(reverse('activation'))
        self.assertEqual(response.status_code, 200)

    def test_get_prefills_email_from_query_param(self):
        response = self.client.get(reverse('activation') + '?email=test@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test@example.com')

    # Unknown email

    def test_unknown_email_redirects_to_done_with_no_email(self):
        """Unknown email: redirect to done, no email sent (neutral response)."""
        response = self.client.post(reverse('activation'), {'email': 'nobody@example.com'})
        self.assertRedirects(response, reverse('activation_done'))
        self.assertEqual(len(mail.outbox), 0)

    # Inactive user

    def test_inactive_user_redirects_to_done_and_receives_activation_email(self):
        """Inactive user: redirect to done, activation link email sent."""
        response = self.client.post(reverse('activation'), {'email': 'inactive@example.com'})
        self.assertRedirects(response, reverse('activation_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['inactive@example.com'])
        # Email contains the activation confirmation URL
        self.assertIn('/accounts/activate/', mail.outbox[0].body)

    # Active user (already activated)

    def test_active_user_redirects_to_done_and_receives_account_exists_email(self):
        """Active user: redirect to done, 'already have account' email with login link."""
        response = self.client.post(reverse('activation'), {'email': 'active@example.com'})
        self.assertRedirects(response, reverse('activation_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['active@example.com'])
        # Email contains login URL, not an activation token URL
        self.assertIn(reverse('login'), mail.outbox[0].body)
        self.assertNotIn('/accounts/activate/', mail.outbox[0].body)

    # Neutral: on-site message is always the same regardless of outcome
    def test_all_outcomes_redirect_to_same_done_url(self):
        """All POST outcomes (known/unknown, active/inactive) redirect to the same URL."""
        for email in ['nobody@example.com', 'inactive@example.com', 'active@example.com']:
            mail.outbox.clear()
            response = self.client.post(reverse('activation'), {'email': email})
            self.assertRedirects(response, reverse('activation_done'), msg_prefix=f'email={email}')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ActivationConfirmViewTests(ActivationRequestViewSetup):
    """Tests for activation_confirm (GET and POST)."""

    # Valid token shows form

    def test_valid_token_get_shows_password_form(self):
        token = _make_token(self.inactive_user, self.site)
        response = self.client.get(reverse('activation_confirm', kwargs={'token': token}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'new_password1')

    # Tampered token shows error

    def test_tampered_token_get_shows_error(self):
        response = self.client.get(
            reverse('activation_confirm', kwargs={'token': 'invalid-tampered-token'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'new_password1')

    def test_token_for_different_site_is_rejected(self):
        """A token issued for a different site cannot activate an account on this site."""
        other_site = Site.objects.create(domain='other.example.com', name='Other')
        token = _make_token(self.inactive_user, other_site)

        response = self.client.get(reverse('activation_confirm', kwargs={'token': token}))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'new_password1')

    # Successful activation

    def test_valid_token_post_activates_user_and_sets_password(self):
        token = _make_token(self.inactive_user, self.site)
        response = self.client.post(
            reverse('activation_confirm', kwargs={'token': token}),
            {'new_password1': 'StrongPass!99', 'new_password2': 'StrongPass!99'},
        )
        self.assertRedirects(response, reverse('activation_complete'))
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.has_usable_password())

    # Race condition: user already active when token is used

    def test_already_activated_user_token_is_rejected_on_post(self):
        """If the user is already activated (has usable password), the activation link cannot be used."""
        # Simulate the user having already activated (e.g. clicked link twice)
        self.inactive_user.set_password('something')
        self.inactive_user.save()

        original_password = self.inactive_user.password
        token = _make_token(self.inactive_user, self.site)

        response = self.client.post(
            reverse('activation_confirm', kwargs={'token': token}),
            {'new_password1': 'NewPass!99', 'new_password2': 'NewPass!99'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'new_password1')

        self.inactive_user.refresh_from_db()
        self.assertEqual(self.inactive_user.password, original_password)
