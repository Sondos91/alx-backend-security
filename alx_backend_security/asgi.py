"""
ASGI config for alx_backend_security project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_security.settings')

application = get_asgi_application()
