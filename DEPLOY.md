# Deploying to PythonAnywhere

The **free tier is sufficient for the read API**. Push notifications need the
$5 Hacker plan, because free accounts can only make outbound requests to a
proxy whitelist and `api.push.apple.com` is not on it. Nothing else here needs
paid. A custom domain also needs Hacker, so the free
`<username>.pythonanywhere.com` host is the starting point.

Footprint is about 100 MB - roughly 66 MB virtualenv, 24 MB scripture, the
rest code. The free 512 MB disk is comfortable.

## 1. Bash console

    git clone https://github.com/theapphideaway/assumption.git
    cd assumption
    python3.11 -m venv venv
    ./venv/bin/pip install -r requirements.txt

The scripture and lectionary data are committed, so the clone brings them.
Nothing needs downloading again.

## 2. Environment

    cd ~/assumption
    python -c "import secrets; print('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(64))" > .env
    echo "DJANGO_DEBUG=0" >> .env
    echo "DJANGO_ALLOWED_HOSTS=<username>.pythonanywhere.com" >> .env
    echo "PARISH_TZ=America/Boise" >> .env
    chmod 600 .env

`.env` is gitignored. Settings raise on startup rather than run with the
development key, so a missing secret fails loudly instead of quietly.

## 3. Database and static files

    ./venv/bin/python manage.py migrate
    ./venv/bin/python manage.py collectstatic --noinput
    ./venv/bin/python manage.py createsuperuser

SQLite for now. Postgres is a paid add-on; set `POSTGRES_DB` and friends and
the settings switch over with no code change.

## 4. Web tab

Create the web app with **Manual configuration** - NOT the Django option,
which scaffolds a fresh project over yours. Choose Python 3.11.

| Field | Value |
|---|---|
| Source code | `/home/<username>/assumption` |
| Working directory | `/home/<username>/assumption` |
| Virtualenv | `/home/<username>/assumption/venv` |
| WSGI file | replace contents with `deploy/wsgi_pythonanywhere.py.template` |

Static files mapping:

| URL | Directory |
|---|---|
| `/static/` | `/home/<username>/assumption/staticfiles` |

Then **Reload**.

## 5. Verify

    curl -s https://<username>.pythonanywhere.com/api/v1/today/ | head -c 400
    curl -s https://<username>.pythonanywhere.com/api/v1/scripture/John/1/ | head -c 200

`/admin/` should render styled. Unstyled means the static mapping is wrong.

## Free-tier housekeeping

Free web apps expire every three months. The Web tab has a **"Run until 3
months from today"** button - click it, and set a reminder, because the app
goes dark silently otherwise.

## When you upgrade

1. Add the parish domain on the Web tab and point DNS at PythonAnywhere.
2. Add it to `DJANGO_ALLOWED_HOSTS` in `.env`.
3. Only then consider `DJANGO_HSTS_SECONDS`. Never enable HSTS on the shared
   `pythonanywhere.com` host - it is effectively irreversible for its duration.
4. Outbound access unlocks, so APNs becomes possible.
