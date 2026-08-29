import os
import sys


def main():
    """Run Django's command-line utility."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "ecommerce_project.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
