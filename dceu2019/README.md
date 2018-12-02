# Dceu2019

Describe your project in one sentence.

## Quickstart

Install the project and the development dependencies into a [virtual environment](https://docs.python.org/3.7/tutorial/venv.html):

```console
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install --editable .[dev]
./manage.py migrate
./manage.py runserver
```

## Starting a New App

First create a new directory in the `apps` directory:

```console
mkdir src/dceu2019/apps/name
```

Then pass the path to the new directory to the [startapp](https://docs.djangoproject.com/en/2.0/ref/django-admin/#django-admin-startapp) command:

```console
./manage.py startapp name src/dceu2019/apps/name
```

## Deployment

The following list describes only the absolute necessary steps to outline a deployment for a Django project wheel. For example a component to serve static files is missing - you could use [WhiteNoise](https://github.com/evansd/whitenoise/) to do this.

Also see [How to use Django with Gunicorn](https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/gunicorn/) and [Deployment Checklist](https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/) for more information.

1.  Add your favorite WSGI HTTP server, e.g.  [Gunicorn](https://gunicorn.org/), to `install_requires` in `setup.cfg`.
2.  [Check](https://github.com/mgedmin/check-manifest) if all files are included in the package:
    ```console
    check-manifest
    ```
3.  [Build](https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives) a [wheel](https://github.com/pypa/wheel) of the project.
    ```console
    ./setup.py bdist_wheel
    ```
4.  Copy the wheel file from the `dist` directory to the server to be deployed.
5.  Create a minimal configuration on the server using environment variables.
    ```bash
    export DJANGO_SETTINGS_MODULE=dceu2019.conf.settings
    export DJANGO_ALLOWED_HOSTS=www.example.com
    export DJANGO_DEBUG=False
    ```
6.  Install the wheel and [collect the static files](https://docs.djangoproject.com/en/2.0/ref/contrib/staticfiles/#django-admin-collectstatic):
    ```console
    python3 -m pip install --find-links=/path/to/wheel_dir dceu2019
    django-project collectstatic --no-input
    ```
7.  Start Gunicorn like this:
    ```console
    gunicorn dceu2019.conf.wsgi
    ```
