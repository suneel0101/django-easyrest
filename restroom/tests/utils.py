import datetime
from restroom.tests.models import (
    Modelo,
    Modelb,
    Modelc,
    ModelAuthed,
    ModelFK,
    ModelFKID,
    ModelM2M,
    DecimalModel)
from django.contrib.auth.models import User
from restroom.models import APIKey


def assert_patterns_are_equal(pattern_x, pattern_y):
    assert len(pattern_x) == len(pattern_y), (
        "X has {} items while Y has {} items".format(
            len(pattern_x), len(pattern_y)))
    fields = ['_callback_str', 'name', '_regex']
    for i in range(len(pattern_x)):
        if not all(
            [getattr(pattern_x[i], field) == getattr(pattern_y[i], field)
             for field in fields]):
            raise AssertionError("The patterns are not equal")
    return True


def prepare_real_modelb(context):
    Modelb.objects.all().delete()

    Modelb.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        timestamp=datetime.datetime(2013, 1, 1, 12),
        awesome=True)

    Modelb.objects.create(
        text='Some more text',
        timestamp=datetime.datetime(2013, 3, 1, 12),
        slug='b-slug',
        awesome=False)


def prepare_real_model(context):
    Modelo.objects.all().delete()

    Modelo.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        awesome=True)

    Modelo.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False)


def prepare_real_modelc(context):
    Modelc.objects.all().delete()

    Modelc.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        awesome=True)

    Modelc.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False)


def prepare_real_model_authed(context):
    ModelAuthed.objects.all().delete()

    ModelAuthed.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        awesome=True)

    ModelAuthed.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False)


def prepare_real_model_fk(context):
    Modelc.objects.all().delete()

    ModelFK.objects.all().delete()
    c1 = Modelc.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        awesome=True)

    c2 = Modelc.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False)

    ModelFK.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        awesome=True,
        foreign=c1)

    ModelFK.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False,
        foreign=c2)


def prepare_real_model_fk_id(context):
    Modelc.objects.all().delete()

    ModelFKID.objects.all().delete()
    c1 = Modelc.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        awesome=True)

    c2 = Modelc.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False)

    ModelFKID.objects.create(
        text='Some text',
        optional_text='Optional text',
        slug='a-slug',
        awesome=True,
        foreign=c1)

    ModelFKID.objects.create(
        text='Some more text',
        slug='b-slug',
        awesome=False,
        foreign=c2)


def prepare_api_key(context):
    User.objects.all().delete()
    APIKey.objects.all().delete()
    user = User.objects.create_user('test_user', 'test@user.com', 'password')
    context.password = 'password'
    api_key = APIKey(user=user)
    api_key.save()
    context.user = user
    context.api_key = api_key


def prepare_real_model_m2m(context):
    ModelM2M.objects.all().delete()
    dec = DecimalModel.objects.create(value=123.24)
    next_dec = DecimalModel.objects.create(value=3.14)
    m2m = ModelM2M(text='awesome m2m')
    m2m.save()
    m2m.many.add(dec)
    m2m.many.add(next_dec)
    m2m.save()
