# Registry

## Install Registry as an app in your project

1. Install using pdm:

    pdm add "git+https://github.com/sevenpastnine/registry.git"

2. Add to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ...
    'registry'
    'django_countries',
    'adminsortable2',
    'widget_tweaks',
    'convenient_formsets',
    'django.contrib.postgres',
]
```

3. Set the following settings:

```python
REGISTRY_PROJECT_NAME = 'My Project'
REGISTRY_URL = 'https://myproject.org'
REGISTRY_EMAIL_SENDER = 'My project <noreply@myproject.org>'
```
