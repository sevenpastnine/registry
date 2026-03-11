from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail

from backend.registry.models import Organisation, Person, Project
from backend.registry.admin_views import create_or_update_person


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class CreateOrUpdatePersonTests(TestCase):
    """Tests for the create_or_update_person import helper."""

    def setUp(self):
        self.site = Site.objects.get_current()
        self.project = Project.objects.create(site=self.site, slug='test-import')
        self.org = Organisation.objects.create(
            name='Test Organisation', short_name='TO', country='DE'
        )
        self.org.sites.add(self.site)

    # Brand-new user

    def test_new_user_created_active_with_unusable_password(self):
        """Brand-new user gets is_active=True and an unusable password."""
        user_created, is_new_to_site = create_or_update_person(
            'Alice', 'Smith', 'alice@example.com', None, self.org, self.site
        )

        self.assertTrue(user_created)
        self.assertTrue(is_new_to_site)

        user = User.objects.get(username='alice@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.has_usable_password())

        person = Person.objects.get(user=user)
        self.assertIn(self.site, person.sites.all())

    # Idempotency

    def test_reimport_creates_no_duplicates(self):
        """Re-importing the same email creates no duplicate User or Person."""
        create_or_update_person('Alice', 'Smith', 'alice@example.com', None, self.org, self.site)
        user_created, is_new_to_site = create_or_update_person(
            'Alice', 'Smith', 'alice@example.com', None, self.org, self.site
        )

        self.assertFalse(user_created)
        self.assertFalse(is_new_to_site)
        self.assertEqual(User.objects.filter(username='alice@example.com').count(), 1)
        self.assertEqual(Person.objects.filter(user__username='alice@example.com').count(), 1)

    # Inactive user from another site

    def test_inactive_user_from_other_site_gains_site_and_stays_inactive(self):
        """Inactive user already on another site: gains current site, stays inactive."""
        other_site = Site.objects.create(domain='other.example.com', name='Other Site')

        user = User.objects.create_user(
            username='bob@example.com', email='bob@example.com', is_active=False
        )
        user.set_unusable_password()
        user.save()
        person = Person.objects.create(user=user)
        person.sites.add(other_site)

        user_created, is_new_to_site = create_or_update_person(
            'Bob', 'Jones', 'bob@example.com', None, self.org, self.site
        )

        self.assertFalse(user_created)
        self.assertTrue(is_new_to_site)

        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertFalse(user.has_usable_password())
        self.assertIn(self.site, person.sites.all())

    # Active user from another site

    def test_active_user_from_other_site_stays_active_and_password_unchanged(self):
        """Active user from another site: stays active, password not touched."""
        other_site = Site.objects.create(domain='other.example.com', name='Other Site')

        user = User.objects.create_user(
            username='carol@example.com',
            email='carol@example.com',
            password='existing-password-123',
        )
        person = Person.objects.create(user=user)
        person.sites.add(other_site)

        # Record the password hash before import
        password_hash_before = user.password

        user_created, is_new_to_site = create_or_update_person(
            'Carol', 'Lee', 'carol@example.com', None, self.org, self.site
        )

        self.assertFalse(user_created)
        self.assertTrue(is_new_to_site)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.has_usable_password())
        self.assertEqual(user.password, password_hash_before)
        self.assertIn(self.site, person.sites.all())

    # No email sent during import

    def test_no_email_sent_when_creating_new_person(self):
        """Importing a person must not send any email."""
        create_or_update_person('Alice', 'Smith', 'alice@example.com', None, self.org, self.site)
        self.assertEqual(len(mail.outbox), 0)
