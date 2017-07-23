"""
Django settings for gods_acre project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mma*a=-f8f@*7aijefemjfly@3epbofcug*^fq5os)6)+30w^z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jet',  # django-jet: has to be before admin
    'admin_reorder',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cemetery',  # mine
    'rosetta',  # django-rosetta

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # auto-detect language preference
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'admin_reorder.middleware.ModelAdminReorder',
]

ROOT_URLCONF = 'gods_acre.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # 'apptemplates.Loader',  # django-apploader
                # 'django.template.loaders.filesystem.Loader',
                # 'django.template.loaders.app_directories.Loader',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gods_acre.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

# guide: https://medium.com/@nolanphillips/a-short-intro-to-translating-your-site-with-django-1-8-343ea839c89b
LANGUAGES = [
    ('en', _('English')),
    ('ro', _('Romanian'))
]

LANGUAGE_CODE = 'ro'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale/')
]

TIME_ZONE = 'Europe/Bucharest'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'


# Model-admin Reorder
# https://github.com/mishbahr/django-modeladmin-reorder
# TODO fix breadcrumb to say "cemetery" at http://127.0.0.1:8000/admin/cemetery/ instead of "general ownership"
ADMIN_REORDER = (
    'auth',

    # General
    {'app': 'cemetery', 'label': _('General'), 'models': [
        {'model': 'cemetery.Spot',              'label': _('Spots')},
    ]},

    # Ownership
    {'app': 'cemetery', 'label': _('Ownership'), 'models': [
        {'model': 'cemetery.Deed',              'label': pgettext_lazy('short', 'Deeds')},
        {'model': 'cemetery.OwnershipReceipt',  'label': _('Receipts')},
        {'model': 'cemetery.Owner',             'label': _('Owners')},
    ]},

    # Operations
    {'app': 'cemetery', 'label': _('Burials'), 'models': [
        {'model': 'cemetery.Operation',         'label': _('Operations')},
    ]},

    # Constructions
    {'app': 'cemetery', 'label': _('Constructions'), 'models': [
        {'model': 'cemetery.Construction',      'label': _('Constructions')},
        {'model': 'cemetery.Authorization',     'label': _('Authorizations')},
        {'model': 'cemetery.Company',           'label': _('Companies')}
    ]},

    # Payments
    {'app': 'cemetery', 'label': _('Payments'), 'models': [
        {'model': 'cemetery.PaymentUnit',       'label': _('Units')},
        {'model': 'cemetery.PaymentReceipt',    'label': _('Receipts')},
    ]},

    # Maintenance
    {'app': 'cemetery', 'label': _('Maintenance'), 'models': [
        {'model': 'cemetery.Maintenance',       'label': _('Maintenances')},
    ]},
)

# django-jet
JET_SIDE_MENU_COMPACT = True  # when False, models for each app will be hidden in a flowing menu

JET_THEMES = [
    # theme folder name; color of the theme's button in user menu; theme title
    {'theme': 'default',        'color': '#47bac1',     'title': 'Default'},
    {'theme': 'green',          'color': '#44b78b',     'title': 'Green'},
    {'theme': 'light-green',    'color': '#2faa60',     'title': 'Light Green'},
    {'theme': 'light-violet',   'color': '#a464c4',     'title': 'Light Violet'},
    {'theme': 'light-blue',     'color': '#5EADDE',     'title': 'Light Blue'},
    {'theme': 'light-gray',     'color': '#222',        'title': 'Light Gray'},
]

JET_SIDE_MENU_ITEMS = [
    {'label': _('Models'), 'app_label': 'cemetery', 'items': [
        {'name': 'spot',            'label': _('Spots')},

        {'name': 'deed',            'label': _('Deeds')},
        {'name': 'ownershipreceipt', 'label': _('Ownership Receipts')},
        {'name': 'owner',           'label': _('Owners')},

        {'name': 'construction',    'label': _('Constructions')},
        {'name': 'authorization',   'label': _('Authorizations')},
        {'name': 'company',         'label': _('Companies')},

        {'name': 'operation',       'label': _('Operations')},

        {'name': 'paymentunit',     'label': _('Payment Units')},
        {'name': 'paymentreceipt',  'label': _('Payment Receipts')},

        {'name': 'maintenance',     'label': _('Maintenance')},
    ]},

    {'label': _('Data'), 'items': [
        {'label': _('Import'), 'url': '/import'}  # FIXME
    ]},
]
