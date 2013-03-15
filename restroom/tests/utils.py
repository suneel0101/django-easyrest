import datetime
from restroom.tests.models import (
    Modelo,
    Modelb,
    Modelc,
    ModelAuthed,
    ModelFK,
    ModelFKID)


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
