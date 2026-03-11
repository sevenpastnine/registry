# Design Document

This document describes the design of key components in the Registry application — the rationale behind decisions, the alternatives considered, and the tradeoffs made. It is intended as a reference for future developers and maintainers.

## Table of Contents

1. [Authentication & Account Activation](#1-authentication--account-activation)
   - [Importing Users and Organisations](#importing-users-and-organisations)
2. [Multiple Project Sites](#2-multiple-project-sites)
3. [Study Design Maps](#3-study-design-maps)

## 1. Authentication & Account Activation

### Overview

Because `django.contrib.sites` is used to serve multiple project sites (see [§2](#2-multiple-project-sites)), a single `User` may be a member of multiple sites via `Person.sites`. Credentials are shared across all sites — a user only ever needs one password. This is communicated explicitly in registration and password-reset emails.

The project uses emails as Django usernames.

User onboarding is a two-phase process:

1. **Import phase** — an admin either uploads an Excel file (bulk) or creates a `Person` record directly in the Django admin (individual). Both paths create `User` accounts with `is_active=True` and an unusable password so that imported People appear immediately in project listings without requiring any prior self-action from the user. See [Importing Users and Organisations](#importing-users-and-organisations).
2. **Activation phase** — the user visits `/accounts/activate/`, submits their email address, and receives a signed link to set their own password, which activates their account. The email is only sent on demand; nothing is sent automatically after import.

This avoids admin-generated passwords being transmitted by email and ensures users always choose their own credentials.

### User states

A user account can be in one of three meaningful states:

| `is_active` | `has_usable_password()` | Meaning |
|---|---|---|
| `True` | `False` | Pending activation — imported but not yet set a password. |
| `True` | `True` | Active — has set their own password and can log in. |
| `False` | any | Suspended by an admin. Cannot log in. |

`is_active` carries only the Django-standard meaning of "account not suspended". The pending/active distinction is expressed exclusively through `has_usable_password()`.

### User states on import

An imported person may be in one of three states. Each is handled differently:

| State | Action |
|---|---|
| Brand-new user (no account anywhere) | Create `User` with `is_active=True` and an unusable password; create `Person`; link to current site. |
| Pending user (imported on another site, not yet activated) | Find existing `User` and `Person`; add current site to their `Person.sites` M2M; leave `is_active` and password untouched. |
| Active user (already activated on another site) | Find existing `User` and `Person`; add current site to their `Person.sites` M2M; leave `is_active` and password untouched. |

The third case is deliberate: the user already has working credentials and there is no reason to invalidate them. They are simply informed that the same credentials work on the new site.

### Activation request flow

`activation_request` (`/accounts/activate/`) intentionally returns the same neutral done page regardless of the outcome (unknown email, inactive user, active user). This prevents user enumeration: an attacker cannot determine whether an email address has an account by observing the response.

The emails sent per outcome are:

| Outcome | Email sent |
|---|---|
| Unknown email (not imported on this site) | None |
| Pending user (imported, not yet activated) | Activation link email (3-day expiry) |
| Active user (already activated) | Account-exists notice with login link and cross-site note |

### Password reset override

Django's built-in password reset flow sends a reset link regardless of whether the account has a usable password. For pending users (who have an unusable password and have never activated), a reset link is meaningless — they need the activation flow instead.

`PasswordResetView.form_valid()` intercepts the POST: if the submitted email belongs to a pending `Person` on the current site (i.e. `has_usable_password()` is `False`), it sends activation instructions and redirects to Django's neutral password-reset done page instead. This preserves account-state privacy while guiding pending users through activation. Active users follow the standard Django reset flow.

### Importing Users and Organisations

#### Excel file structure

The bulk import expects a single `.xlsx` workbook with two sheets, processed in order. Column names are matched by header value (order does not matter). All columns are required unless noted.

##### Sheet: `Organisations`

| Column | Description |
|---|---|
| `Short name` | Unique identifier used to reference the organisation from the People sheet. |
| `Name` | Full display name. |
| `Country` | Country full name as recognised by `django-countries` (e.g. `Netherlands`, `United Kingdom`). |

Rows with any empty required cell are silently skipped. An unrecognised country name produces a per-row error and the row is skipped; all other rows in the transaction continue.

##### Sheet: `People`

| Column | Description |
|---|---|
| `First name` | Person's first name. |
| `Last name` | Person's last name. |
| `Email` | Email address — used as the Django username. Must be a valid email. |
| `Organisation (short)` | Must match the `Short name` of an organisation already in the database or imported in the same file. |
| `ORCID` | ORCID identifier (optional). Leave blank if not known. |

Rows with any empty required cell (all columns except `ORCID`) are silently skipped. An invalid email or an unrecognised organisation short name produces a per-row error and the row is skipped.

#### Transaction behaviour

Both sheets are processed inside a single database transaction. If any row produces an error, the error is recorded and displayed after the import attempt. The transaction is rolled back only if there are errors — a clean run with no errors commits all changes atomically.

#### Direct admin entry

Individual people and organisations can be created directly in the Django admin without using the import. The same three-state logic applies: creating a `User` + `Person` manually with `is_active=True` and an unusable password (by unchecking **Password-based authentication** on the add-user form) will allow the person to appear in listings and trigger the self-activation flow when they request access.

## 2. Multiple Project Sites

_To be documented._

## 3. Study Design Maps

_To be documented._
