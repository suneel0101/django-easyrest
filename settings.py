INSTALLED_APPS = (
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

ROOT_URLCONF = 'tests.urls'
