import os
import sys

import django

if __name__ == "__main__":
    # insert here whatever commands you use to run daphne
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

    sys.argv = ["daphne", "config.asgi:application"]
    from daphne.cli import CommandLineInterface

    django.setup()
    CommandLineInterface.entrypoint()
