INSTALLED_APPS = (
    'unclebob',
    'restroom',
)

TEST_RUNNER = 'unclebob.runners.Nose'
import unclebob
unclebob.take_care_of_my_tests()

UNCLEBOB_EXTRA_NOSE_ARGS = [
    '--verbosity=2',
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
