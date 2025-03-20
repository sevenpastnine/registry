import string
import random
import openpyxl

from backend.utils import get_current_site
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mass_mail
from django.conf import settings

from django_countries import countries

from . import models
from . import admin_forms as forms


def get_new_user_email_message(name, email, password, site_name, site_url, support_email):
    return f'''
Dear {name},

You have been added to the {site_name} Registry.

You can access the Registry at {site_url}

Your username is: {email}
Your password is: {password}

In case you have any questions or run into problems, please contact us at {support_email}


Best regards,

The {site_name} Registry team
'''


def get_existing_user_email_message(name, site_name, site_url, support_email):
    return f'''
Dear {name},

You have been added to the {site_name} Registry.

You can access the Registry at {site_url}

Please log in with your existing Registry credentials.

In case you have any questions or run into problems, please contact us at {support_email}


Best regards,

The {site_name} Registry team
'''


def check_import_people_permission(admin, request):
    """
    Check if the user has permission to import people.
    Returns (has_permission, redirect_response)
    """
    # Superusers and staff with is_admin=True can always import
    if request.user.is_superuser or (request.user.is_staff and getattr(request.user, 'is_admin', False)):
        return True, None

    # Check if the user has permission to add/change users
    if not request.user.has_perm('auth.add_user') or not request.user.has_perm('auth.change_user'):
        messages.error(request, "You don't have permission to import people. You need user add/change permissions.")
        return False, redirect('admin:registry_person_changelist')

    # Also check permission to add/change Person model
    if not admin.has_add_permission(request) or not admin.has_change_permission(request):
        messages.error(request, "You don't have permission to add or change people in this registry.")
        return False, redirect('admin:registry_person_changelist')

    return True, None


def process_organisations_sheet(sheet, current_site, request):
    """Process organizations from Excel sheet"""
    headers = [cell.value for cell in sheet[1]]  # Get header row

    # Column indices
    short_name_idx = headers.index('Short name')
    name_idx = headers.index('Name')
    country_idx = headers.index('Country')

    org_count = 0

    for row in list(sheet.rows)[1:]:  # Start from row 2 (skip header)
        short_name = str(row[short_name_idx].value or '').strip()
        name = str(row[name_idx].value or '').strip()
        country_name = str(row[country_idx].value or '').strip()

        if not (short_name and name and country_name):
            continue

        try:
            country_code = countries.by_name(country_name)
            if not country_code:
                messages.error(request, f"Country not found: {country_name}")
                continue

            org, created = models.Organisation.objects.update_or_create(
                short_name=short_name,
                defaults={
                    'name': name,
                    'country': country_code
                }
            )

            # Add to current site
            if current_site not in org.sites.all():
                org.sites.add(current_site)

            org_count += 1
        except Exception as e:
            messages.error(request, f"Error processing organisation {name}: {str(e)}")

    return org_count


def get_person_name(first_name, last_name, email):
    """Determine display name for email messages"""
    if first_name:
        return first_name
    elif last_name:
        return last_name
    return email


def process_people_sheet(sheet, current_site, site_name, site_url, request):
    """Process people from Excel sheet"""
    headers = [cell.value for cell in sheet[1]]  # Get header row

    # Find column indices
    orcid_idx = headers.index('ORCID')
    org_idx = headers.index('Organisation (short)')
    first_name_idx = headers.index('First name')
    last_name_idx = headers.index('Last name')
    email_idx = headers.index('Email')

    people_count = 0
    new_user_emails = []
    existing_user_emails = []

    for row in list(sheet.rows)[1:]:
        orcid = str(row[orcid_idx].value or '').strip() if orcid_idx is not None and row[orcid_idx].value else None
        org_short_name = str(row[org_idx].value or '').strip()
        first_name = str(row[first_name_idx].value or '').strip()
        last_name = str(row[last_name_idx].value or '').strip()
        email = str(row[email_idx].value or '').strip()

        if not (first_name and last_name and email and org_short_name):
            continue

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, f'Invalid email address: {email}')
            continue

        # Find organisation
        try:
            org = models.Organisation.objects.get(short_name=org_short_name)
        except models.Organisation.DoesNotExist:
            messages.error(request, f'Organisation {org_short_name} not found for person {email}')
            continue

        # Create or update user and person
        password, user_created, is_new_to_site = create_or_update_person(
            first_name, last_name, email, orcid, org, current_site
        )

        # Prepare email notifications
        person_name = get_person_name(first_name, last_name, email)

        if user_created:
            # New user gets credentials
            email_content = get_new_user_email_message(
                person_name, email, password, site_name, site_url, settings.REGISTRY_SUPPORT_EMAIL
            )
            new_user_emails.append((
                f'You have been added to {site_name} Registry',
                email_content,
                settings.REGISTRY_SUPPORT_EMAIL,
                [email]
            ))
        elif is_new_to_site:
            # Existing user gets notification about new site
            email_content = get_existing_user_email_message(
                person_name, site_name, site_url, settings.REGISTRY_SUPPORT_EMAIL
            )
            existing_user_emails.append((
                f'You have been added to {site_name} Registry',
                email_content,
                settings.REGISTRY_SUPPORT_EMAIL,
                [email]
            ))

        people_count += 1

    return people_count, new_user_emails, existing_user_emails


def create_or_update_person(first_name, last_name, email, orcid, org, current_site):
    """Create or update user and person records"""
    # Generate random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    # Create or update user
    user, user_created = User.objects.update_or_create(
        username=email,
        defaults={
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }
    )

    if user_created:
        user.set_password(password)
        user.save()

    # Create or update person
    person, person_created = models.Person.objects.update_or_create(
        user=user,
        defaults={'orcid': orcid}
    )

    # Add to organisation
    if org not in person.organisations.all():  # type: ignore
        person.organisations.add(org)  # type: ignore

    # Check if person is already in site
    is_new_to_site = current_site not in person.sites.all()

    # Add to current site
    if is_new_to_site:
        person.sites.add(current_site)

    return password, user_created, is_new_to_site


def import_people(admin, request):
    # Check permissions
    has_permission, redirect_response = check_import_people_permission(admin, request)
    if not has_permission:
        return redirect_response

    current_site = get_current_site(request)
    site_name = current_site.name
    site_url = f"https://{current_site.domain}" if current_site.domain.startswith('http') else f"https://{current_site.domain}"

    if request.method == 'POST':
        form = forms.PersonImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            try:
                # Process the Excel file
                with transaction.atomic():
                    workbook = openpyxl.load_workbook(file)

                    # Process organisations sheet
                    org_sheet = workbook['Organisations']
                    org_count = process_organisations_sheet(org_sheet, current_site, request)

                    # Process people sheet
                    people_sheet = workbook['People']
                    people_count, new_user_emails, existing_user_emails = process_people_sheet(
                        people_sheet, current_site, site_name, site_url, request
                    )

                    # If there were any errors, abort the transaction
                    if messages.get_messages(request):
                        raise Exception()

                # Send email notifications
                all_emails = new_user_emails + existing_user_emails
                if all_emails:
                    send_mass_mail(all_emails, fail_silently=False)

                email_count = len(all_emails)
                messages.success(request, f'Successfully imported {org_count} organisations and {people_count} people.')
                messages.success(request, f'Sent {email_count} email notifications.')

                return redirect('..')
            except Exception as e:
                if str(e):
                    messages.error(request, f'Error during import: {str(e)}')
    else:
        form = forms.PersonImportForm()

    return render(request, 'admin/registry/person/import.html', {
        'form': form,
        'title': 'Import People and Organisations',
        'opts': admin.model._meta,
        'app_label': admin.model._meta.app_label,
        'has_view_permission': admin.has_view_permission(request),
        'has_add_permission': admin.has_add_permission(request),
        'has_change_permission': admin.has_change_permission(request),
    })
