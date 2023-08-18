"""
WSGI config for real_estate_listings project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import socket
from django.core.wsgi import get_wsgi_application

ipaddress = socket.gethostbyname(socket.gethostname())
#local = ipaddress == '127.0.1.1' or ipaddress == '192.168.0.46'
local = False#robie tunelowanie ngrok z localhosta na dostępny w internecie adres
settings_path = 'real_estate_listings.settings.local' if local else 'real_estate_listings.settings.production'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_path)

application = get_wsgi_application()
