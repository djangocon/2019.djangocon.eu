import os
import sys
from django.core.management.utils import get_random_secret_key

# Use everything from settings.local, write a minimal template if it does not
# exist and alert user.
try:
    from .local import *
except ImportError:
    sys.stderr.write(
        "Could not find settings.local, creating a default one. Please "
        "customize it with your SECRET_KEY, DATABASES etc. and start again.\n"
    )
    default = (
        """# Using development settings, replace in production!\n"""
        """from .dev import *  # noqa\n"""
        """\n"""
        """SECRET_KEY = "{secret_key}"\n"""
        """DATABASES = DATABASES = {{\n"""
        """    "default": {{\n"""
        """        "ENGINE": "django.db.backends.sqlite3",\n"""
        """        "NAME": str(BASE_DIR.parent.parent / "db.sqlite3"),\n"""
        """    }}\n"""
        """}}\n"""
    ).format(
        secret_key=get_random_secret_key()
    )
    f = open(os.path.join(os.path.dirname(__file__), "local.py"), "w")
    f.write(
        default
    )
    sys.exit(1)
