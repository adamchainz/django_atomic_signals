import os

ADMINS = ()


database_implementation = os.getenv('DATABASE', 'sqlite3')

if database_implementation == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'django_atomic_signals.db',
        }
    }
elif database_implementation == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'django_mysql',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            'OPTIONS': {'charset': 'utf8mb4'},
            'TEST': {
                'COLLATION': "utf8mb4_general_ci",
                'CHARSET': "utf8mb4"
            }
        }
    }

SECRET_KEY = '_uobce43e5osp8xgzle*yag2_16%y$sf*5(12vfg25hpnxik_*'

INSTALLED_APPS = (
    'django_atomic_signals',
    'tests',
    'django_nose',
)

DEBUG = True

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

MIDDLEWARE_CLASSES = ()
