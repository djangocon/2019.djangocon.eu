Getting started
===============

Here is the main parts of this project's structure::

.
├── dceu2019
│   ├── db.sqlite3  # <= NOT in repo
│   ├── __init__.py
│   ├── manage.py
│   ├── MANIFEST.in
│   ├── media
│   ├── README.md
│   ├── setup.cfg
│   ├── setup.py
│   ├── src
│   │   ├── dceu2019
│   │   │   ├── apps
│   │   │   │   └── __init__.py
│   │   │   ├── __init__.py
│   │   │   ├── locale
│   │   │   ├── settings
│   │   │   │   ├── base.py
│   │   │   │   ├── dev.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── local.py  # <= NOT in repo
│   │   │   │   ├── pretalx.py
│   │   │   │   └── production.py
│   │   │   ├── static
│   │   │   ├── templates
│   │   │   ├── urls.py
│   │   │   └── wsgi.py
│   │   └── __init__.py
│   └── staticfiles
│       └── ...
├── hugo_project
│   └── ...


The first, ``dceu2019`` contains a Django project and ``hugo_project`` contains
the `Hugo project <https://gohugo.io/>`__ for static site generation (the main
site).

We use a **static main site** because we want to archive the main conference
website as easily as possible. We are using the default version of Hugo for
Ubuntu 18.04, so to generate and run the main site, just do:

.. code-block:: console

  # Install Hugo
  $ sudo apt install hugo

  # Go to project directory
  $ cd hugo_project

  # Run dev server
  $ hugo server


The **Django project** will be used before and during the conference for
planning purposes: Talk submissions, scheduling, and ticket holder services such
as ride sharing and accommodation sharing.

You can install and work on a development version following these steps:

.. code-block:: console

  # Create a Python 3.6+ virtualenv (virtualenvwrapper)
  $ mkvirtualenv -p python3
  
  # Install project & dependencies in "editable" mode (-e), with the [dev]
  # dependency subset.
  $ pip install -e "dceu2019[dev]"
  
  # Try invoking the Django main management script
  $ python dceu2019/manage.py

  # ...you will be told that it has created a local.py file. You might want to
  # edit this now or later depending on your needs.
  
  # When ready, run migrations.
  $ python dceu2019/manage.py migrate

  # Initialize PreTalx: Creates a superuser etc.
  $ python dceu2019/manage.py init

  # Now you can run the development server
  $ python dceu2019/manage.py runserver

  # Point your browser to localhost:8000/pretalx and you'll see an empty
  # schedule

