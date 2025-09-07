"""
WSGI config for alx_backend_security project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_security.settings')

application = get_wsgi_application()
