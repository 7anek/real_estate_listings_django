#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
# import socket
import requests


def get_environment():
    environment=os.environ.get("ENVIRONMENT",False)
    if environment:
        if environment == "development":
            return 'real_estate_listings.settings.local'
        elif environment == "staging":
            return 'real_estate_listings.settings.staging'
        elif environment == "production":
            return 'real_estate_listings.settings.production'
        else:
            return False
    else:
        return False
    # try:
    #     response = requests.get(f"https://{os.environ.get('NGROK_URL')}")
    #     return response.status_code != 404
    # except requests.exceptions.RequestException:
    #     return False

def main():
    """Run administrative tasks."""
    # ipaddress = socket.gethostbyname(socket.gethostname())
    # local = ipaddress == '127.0.1.1' or ipaddress == '192.168.0.46'
    # settings_path = 'real_estate_listings.settings.production' if check_production() else 'real_estate_listings.settings.local'
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_path)
    environment=get_environment()
    if environment:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', environment)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


