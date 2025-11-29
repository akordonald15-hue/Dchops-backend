# dev.py

from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORS for local dev
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # your frontend local dev
]
CORS_ALLOW_CREDENTIALS = True

# JWT cookie secure flag for dev
SIMPLE_JWT['AUTH_COOKIE_SECURE'] = False
SIMPLE_JWT['AUTH_COOKIE_SAMESITE'] = 'Lax'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True) == True
EMAIL_USE_SSL = env.bool('EMAIL_USE_SSL', default=False) 
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='akordonald15@gmail.com')
