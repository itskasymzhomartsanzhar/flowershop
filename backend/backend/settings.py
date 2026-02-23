from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

#DATACHANGE RANDOM
SECRET_KEY = 'django-insecure-d5lc8wkd0=l3zfhx68&6u2cqdukh-(q^k8gl0z=&zz=(!f=dv+'

DEBUG = 'True'

#DATACHANGE
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "swiftstore_backend", "flowershop.swifttest.ru" "backend"]

#DATACHANGE
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:8000',
    'https://flowershop.swifttest.ru',

]
#DATACHANGE
BOT_TOKEN = os.getenv('BOT_TOKEN', '7898807263:AAEVGakrVXbQxLXE7jeMTThmruE0ZXz9RBE')
YOOKASSA_ACCOUNT_ID = os.getenv('YOOKASSA_ACCOUNT_ID', '1134900')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY', 'test_KuPzb4yyMFfgEfEYnfJ4gWO8QQtFTzA6TSqCaK3LuAs')
PAYMENT_RETURN_URL = os.getenv('PAYMENT_RETURN_URL', 'https://swiftstore.tw1.su/')
ORDER_ASSEMBLERS_CHAT_ID = os.getenv('ORDER_ASSEMBLERS_CHAT_ID', '')
MOCK_PAYMENT_BUTTON = os.getenv('MOCK_PAYMENT_BUTTON', 'True').lower() == 'true'
DADATA_API_TOKEN = "a1692950cea356040f39b7ff8dfb33b0642c0472"
DADATA_BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)
CORS_ALLOW_HEADERS = (
    'content-disposition',
    'accept-encoding',
    'content-type',
    'accept',
    'origin',
    'Authorization',
    'access-control-allow-methods',
    'initData'
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'backend.middleware.TelegramDataMiddleware'
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Production (PostgreSQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'swiftstore_db',
#         'USER': 'swiftstore_user',
#         'PASSWORD': 'swiftstore_password',
#         'HOST': 'db',
#         'PORT': '5432',
#     }
# }


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        # Local development fallback (when Django runs outside Docker)
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0'))
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', CELERY_BROKER_URL)
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_ALWAYS_EAGER = os.getenv('CELERY_TASK_ALWAYS_EAGER', 'False').lower() == 'true'
CELERY_TASK_TIME_LIMIT = 30
CELERY_TASK_SOFT_TIME_LIMIT = 20

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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Respect reverse proxy headers in production (Nginx -> Django)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Temporary switch: force https in generated media URLs when needed in production
FORCE_HTTPS_MEDIA = os.getenv('FORCE_HTTPS_MEDIA', 'False').lower() == 'true'
