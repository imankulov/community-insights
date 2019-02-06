import environ
import pathlib

BASE_DIR = pathlib.Path(__file__).absolute().parent.parent
env = environ.Env(DEBUG=(bool, False))

if (BASE_DIR / '.env').exists():
    environ.Env.read_env(str(BASE_DIR / '.env'))

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
ALLOWED_HOSTS = [env('ALLOWED_HOST')]

# CloudFlare-proxy specific setting.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'django_celery_beat',
    'insights.core',
    'insights.meetup',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'insights.urls'

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

WSGI_APPLICATION = 'insights.wsgi.application'
DATABASES = {
    'default': env.db(),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = str(BASE_DIR / 'staticfiles')
STATIC_URL = '/static/'

# -----------------------------------------------------------------------------
# Celery settings
# -----------------------------------------------------------------------------
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='foo')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_BEAT_SCHEDULE = {}

# -----------------------------------------------------------------------------
# meetup.com settings
# -----------------------------------------------------------------------------
# OAuth key and secret for API connections
MEETUP_OAUTH_CLIENT_ID = env('MEETUP_OAUTH_CLIENT_ID')
MEETUP_OAUTH_CLIENT_SECRET = env('MEETUP_OAUTH_CLIENT_SECRET')

# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Settings to create superuser
# -----------------------------------------------------------------------------
ADMIN_USERNAME = env('ADMIN_USERNAME')
ADMIN_EMAIL = env('ADMIN_EMAIL')
ADMIN_PASSWORD = env('ADMIN_PASSWORD')

# -----------------------------------------------------------------------------
# Google Cloud settings
# -----------------------------------------------------------------------------
BIGQUERY_DATASET_ID = env('BIGQUERY_DATASET_ID')
