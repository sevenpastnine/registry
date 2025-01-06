import csv

from django_docopt_command import DocOptCommand

from django.core.mail import send_mass_mail

from ... import importer

import logging
logger = logging.getLogger('management.commands')


DOCS = '''
Usage:
    registry import <organisations.csv> <people.csv> [--init] [--traceback]
    registry sendcredentials <people.csv> [--traceback]
'''

REGISTRY_PROJECT_NAME = 'Registry'
REGISTRY_URL = 'https://registry.sevenpastnine.com/'
REGISTRY_EMAIL_SENDER = 'Registry <noreply@sevenpastnine.com>'


class Command(DocOptCommand):
    docs = DOCS

    def handle_docopt(self, args):
        if args['import']:
            importer.run(args['<organisations.csv>'], args['<people.csv>'], args['--init'])
        elif args['sendcredentials']:
            send_credentials(args['<people.csv>'])


def get_message(name, email, password):
    return f'''
Dear {name},

You have been added to the {REGISTRY_PROJECT_NAME} Registry.

You can access the registry at {REGISTRY_URL}

Your username is {email}
Your password is {password}

In case you have any questions or run into problems, please contact Thomas Exner at thomas.exner@sevenpastnine.com


Best regards,

The {REGISTRY_PROJECT_NAME} Registry team
'''


def get_emails(people_csv):
    with open(people_csv) as csvfile:
        reader = csv.reader(csvfile)
        reader.__next__()  # skip header
        for row in reader:
            (password, orcid, organisation, first_name, last_name, email) = [col.strip() for col in row]

            yield (
                f'Your {REGISTRY_PROJECT_NAME} Registry credentials',
                get_message(first_name, email, password),
                REGISTRY_EMAIL_SENDER,
                [email]
            )


def send_credentials(people_csv):
    send_mass_mail(get_emails(people_csv), fail_silently=False)
