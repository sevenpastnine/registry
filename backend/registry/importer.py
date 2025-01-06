import csv
from django_countries import countries

from django.contrib.auth.models import User

from .models import (
    Person,
    PersonRole,
    Organisation,
    Group,
    License,
    ResourceStatus,
    Resource,
    StudyDesign,
)

PERSON_ROLES = [
    'Owner / Main contact',
    'Contributor'
]

USE_CASES = [
]

LICENSES = [
    ('CC-BY-4.0', 'Creative Commons Attribution 4.0 License', 'https://creativecommons.org/licenses/by/4.0/'),
    ('CC-BY-SA-4.0', 'Creative Commons Attribution Share Alike 4.0 License', 'https://creativecommons.org/licenses/by-sa/4.0/'),
    ('CC-BY-ND-4.0', 'Creative Commons Attribution No Deriveratives 4.0 License', 'https://creativecommons.org/licenses/by-nd/4.0/'),
    ('CC-BY-NC-4.0', 'Creative Commons Attribution Non Commercial 4.0 License', 'https://creativecommons.org/licenses/by-nc/4.0/'),
    ('CC-BY-NC-SA-4.0', 'Creative Commons Attribution Non Commercial Share Alike 4.0 License', 'https://creativecommons.org/licenses/by-nc-sa/4.0/'),
    ('CC-BY-NC-ND-4.0', 'Creative Commons Attribution Non Commercial No Deriveratives 4.0', 'https://creativecommons.org/licenses/by-nc-nd/4.0/'),
]

RESOURCE_STATUSES = [
    'Scheduled',
    'In progress',
    'Version for internal review',
    'Internally reviewed (as final dissemination)',
    'Internally reviewed (independent external validation/publication planned)',
    'Under external validation',
    'Publication in preparation',
    'Pre-print / grey publication (as final dissemination)',
    'Published in peer-reviewed journal / validated',
]


def initialize():
    StudyDesign.objects.all().delete()
    Resource.objects.all().delete()
    ResourceStatus.objects.all().delete()
    License.objects.all().delete()
    Group.objects.all().delete()
    Organisation.objects.all().delete()
    PersonRole.objects.all().delete()
    Person.objects.filter(user__is_superuser=False).delete()
    User.objects.filter(is_superuser=False).delete()


def run(organisations_csv, people_csv, init=False):
    if init:
        initialize()

    with open(organisations_csv) as csvfile:
        reader = csv.reader(csvfile)
        reader.__next__()  # skip header
        for row in reader:
            (short_name, country, name) = [col.strip() for col in row]
            Organisation.objects.update_or_create(
                name=name,
                defaults={
                    'short_name': short_name,
                    'country': countries.by_name(country)})

    with open(people_csv) as csvfile:
        reader = csv.reader(csvfile)
        reader.__next__()  # skip header
        for row in reader:
            (password, orcid, organisation, first_name, last_name, email) = [col.strip() for col in row]
            user, created = User.objects.update_or_create(
                username=email,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name})
            user.set_password(password)
            user.save()
            person, created = Person.objects.update_or_create(
                user=user,
                defaults={'orcid': orcid if orcid else None})
            person.organisations.add(Organisation.objects.get(short_name=organisation))  # type: ignore

    for name in PERSON_ROLES:
        PersonRole.objects.get_or_create(name=name)

    for name in USE_CASES:
        Group.objects.get_or_create(name=name)

    for (name, description, url) in LICENSES:
        License.objects.update_or_create(name=name, defaults={
            'description': description,
            'url': url})

    for name in RESOURCE_STATUSES:
        ResourceStatus.objects.get_or_create(name=name)
