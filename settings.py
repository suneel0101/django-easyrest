INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'unclebob',
    'restroom',
    'restroom.tests',
)

TEST_RUNNER = 'unclebob.runners.Nose'
import unclebob
unclebob.take_care_of_my_tests()

UNCLEBOB_EXTRA_NOSE_ARGS = [
    '--verbosity=3',
    '--with-coverage',
    '--cover-package=restroom',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

ROOT_URLCONF = 'restroom.tests.urls'
