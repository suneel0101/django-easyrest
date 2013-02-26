import json

from sure import expect

from django.test.client import Client
from django.core.urlresolvers import reverse

from tests.models import CrazyModel

client = Client()

to_python = json.loads


def test_GET_crazymodel_empty():
    CrazyModel.objects.all().delete()
    res = client.get(reverse('tests_crazymodel_list_api'))
    expect(to_python(res.content)).to.equal([])


def test_GET_crazymodel_paginated():
    CrazyModel.objects.all().delete()
    for i in xrange(0, 40):
        CrazyModel.objects.create(
            text="cool text {}".format(i),
            title="cool title {}".format(i)
        )
    res = client.get(reverse('tests_crazymodel_list_api'),
                     {'page': '1'})

    expected_data_first_five = [
        {u'text': u'cool text 0', u'expired': False, u'id': 1},
        {u'text': u'cool text 1', u'expired': False, u'id': 2},
        {u'text': u'cool text 2', u'expired': False, u'id': 3},
        {u'text': u'cool text 3', u'expired': False, u'id': 4},
        {u'text': u'cool text 4', u'expired': False, u'id': 5}]
    (expect(to_python(res.content))
     .to.equal(expected_data_first_five))

    next_res = client.get(reverse('tests_crazymodel_list_api'),
                     {'page': '3'})

    expected_data_third_five = [
        {u'text': u'cool text 10', u'expired': False, u'id': 11},
        {u'text': u'cool text 11', u'expired': False, u'id': 12},
        {u'text': u'cool text 12', u'expired': False, u'id': 13},
        {u'text': u'cool text 13', u'expired': False, u'id': 14},
        {u'text': u'cool text 14', u'expired': False, u'id': 15}]
    (expect(to_python(next_res.content))
     .to.equal(expected_data_third_five))

    out_of_bounds_res = client.get(reverse('tests_crazymodel_list_api'),
                                   {'page': '10'})

    expect(to_python(out_of_bounds_res.content)).to.equal([])

    CrazyModel.objects.all().delete()


def test_GET_crazymodel_queried():
    CrazyModel.objects.all().delete()
    for i in xrange(0, 40):
        CrazyModel.objects.create(
            text="cool text {}".format(i),
            title="cool title {}".format(i)
        )
    res = client.get(
        reverse('tests_crazymodel_list_api'),
        {'filters': '[{"field": "id", "operator": "in", "value": [1, 2, 4, 5, 8, 12, 16, 18]}, {"field": "title", "operator": "icontains", "value": "cool"}]'
         }
    )
    expected_invalid_field_error = {u'error': u'title is an invalid field'}

    (expect(to_python(res.content))
     .to.equal(expected_invalid_field_error))

    valid_res = client.get(
        reverse('tests_crazymodel_list_api'),
        {'filters': '[{"field": "id", "operator": "in", "value": [1, 2, 4, 5, 8, 12, 16, 18]}, {"field": "text", "operator": "icontains", "value": "cool"}]'
         }
    )

    expected_data_first_five = [
        {u'text': u'cool text 0', u'expired': False, u'id': 1},
        {u'text': u'cool text 1', u'expired': False, u'id': 2},
        {u'text': u'cool text 3', u'expired': False, u'id': 4},
        {u'text': u'cool text 4', u'expired': False, u'id': 5},
        {u'text': u'cool text 7', u'expired': False, u'id': 8}]

    (expect(to_python(valid_res.content))
     .to.equal(expected_data_first_five))

    last_three_res = client.get(
        reverse('tests_crazymodel_list_api'),
        {'filters': '[{"field": "id", "operator": "in", "value": [1, 2, 4, 5, 8, 12, 16, 18]}, {"field": "text", "operator": "icontains", "value": "cool"}]',
         'page': 2,
         }
    )

    expected_data_last_three = [
        {u'text': u'cool text 11', u'expired': False, u'id': 12},
        {u'text': u'cool text 15', u'expired': False, u'id': 16},
        {u'text': u'cool text 17', u'expired': False, u'id': 18}]

    (expect(to_python(last_three_res.content))
     .to.equal(expected_data_last_three))

    CrazyModel.objects.all().delete()


def test_POST_crazymodel():
    CrazyModel.objects.all().delete()
    res = client.post(reverse('tests_crazymodel_list_api'),
                      {'text': 'POST text yo'})
    expect(to_python(res.content)).to.equal(
        {"text": "POST text yo", "expired": False, "id": 1})
    CrazyModel.objects.all().delete()


def test_PUT_crazymodel():
    CrazyModel.objects.all().delete()
    # create a CrazyModel instance
    initial_res = client.post(reverse('tests_crazymodel_list_api'),
                              {'text': 'POST text yo'})

    expect(to_python(initial_res.content)).to.equal(
        {"text": "POST text yo", "expired": False, "id": 1})

    final_res = client.put(
        reverse('tests_crazymodel_single_item_api', kwargs={'_id': 1}),
        {'text': 'PUT text yo'})
    expect(to_python(final_res.content)).to.equal(
        {"text": "PUT text yo", "expired": False, "id": 1})
    CrazyModel.objects.all().delete()


def test_DELETE_crazymodel():
    CrazyModel.objects.all().delete()
    new_model = CrazyModel.objects.create(text='new model')
    _id = new_model.id

    res = client.delete(reverse('tests_crazymodel_single_item_api',
                        kwargs={'_id': _id}))

    expect(to_python(res.content)).to.equal(
        {u'status': u'deletion successful'})
    CrazyModel.objects.all().delete()
