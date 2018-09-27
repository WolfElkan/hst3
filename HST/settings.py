"""
Django settings for HST project.
Generated by 'django-admin startproject' using Django 1.10.3.
For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

from . import ignored

from django.core.mail.backends.smtp import EmailBackend

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ignored.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ignored.DEBUG

CURRENT_HOST = ignored.NGROK_URL

ALLOWED_HOSTS = [CURRENT_HOST,u'localhost',u'www.families.hstonline.org', u'families.hstonline.org']

# Application definition

INSTALLED_APPS = [
    'apps.main',
    'apps.payment',
    'apps.people',
    'apps.program',
    'apps.radmin',
    'apps.rest',
    'apps.reports',
    'apps.old',
    'easy_pdf',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_mysql',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'HST.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'HST.wsgi.application'

class CustomEmailBackend(EmailBackend):
    """docstring for CustomEmailBackend"""
    def __init__(self, **kwargs):
        super(CustomEmailBackend, self).__init__(**kwargs)
    def rsplit(**kwargs):
        print kwargs

# https://stackoverflow.com/questions/21563227/django-allauth-example-errno-61-connection-refused
# https://stackoverflow.com/questions/28074127/django-send-email-shows-success-but-no-email-received
EMAIL_BACKEND = CustomEmailBackend

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': ignored.DB_NAME,
        'USER': ignored.DB_USER,
        'PASSWORD': ignored.DB_PASSWORD,
        'HOST': ignored.DB_HOST,
        'PORT': ignored.DB_PORT,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"
        },
    },
    # 'postgres': {},
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern' # Rockville, MD, USA

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.dirname(BASE_DIR) + '/static/'

PAYPAL_BUSINESS_EMAIL = ignored.PAYPAL_BUSINESS_EMAIL
