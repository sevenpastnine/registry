import datetime
from pathlib import Path
from fabric import Connection, task

SLUG = "registry"
MEDIA = "var/media/"
DESTDIR = Path("/var/projects", SLUG)
HOST = "www@seven.sevenpastnine.com"

c = Connection(HOST)


# -----------------------------------------------------------------------------
# Deploy

@task
def deploy(_):
    c.run(f"cd {DESTDIR} && git pull")
    c.run(f"cd {Path(DESTDIR, 'deployment')} && docker compose up --build --detach", pty=True)


# -----------------------------------------------------------------------------
# Fixtures

@task
def create_fixtures(_):
    c.local("./manage.py dumpdata auth --indent 2 > var/fixtures/auth.json")
    c.local("./manage.py dumpdata sites --indent 2 > var/fixtures/sites.json")
    c.local("./manage.py dumpdata registry --indent 2 > var/fixtures/registry.json")


@task
def load_fixtures(_):
    try:
        c.local(f"dropdb {SLUG}")
    except Exception:
        pass

    c.local(f"createdb --template=template0 --locale=en_US.UTF-8 {SLUG}")

    c.local("./manage.py migrate")
    c.local("./manage.py loaddata var/fixtures/auth.json")
    c.local("./manage.py loaddata var/fixtures/sites.json")
    c.local("./manage.py loaddata var/fixtures/registry.json")


# -----------------------------------------------------------------------------
# Sync

@task
def sync(_):
    syncdb(_)
    syncmedia(_)


@task
def syncdb(_):
    fn = "{}-{}.sql.gz".format(SLUG, str(datetime.datetime.now()).replace(" ", "-"))

    c.run(f"pg_dump {SLUG} | gzip -c > {fn}")
    c.get(fn, fn)
    c.run(f"rm {fn}")

    try:
        c.local(f"dropdb {SLUG}")
    except Exception:
        pass

    c.local(f"createdb --template=template0 --locale=sl_SI.UTF-8 {SLUG}")

    c.local(f"gunzip -c {fn} | psql -f - {SLUG}")
    c.local(f"rm {fn}")


@task
def syncmedia(_):
    c.local(f"rsync -av --delete {HOST}:{DESTDIR}/{MEDIA} {MEDIA}/")

# -----------------------------------------------------------------------------
