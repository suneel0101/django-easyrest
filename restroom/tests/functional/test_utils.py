from sure import expect, scenario
from restroom.tests.models import DecimalModel
from restroom.tests.utils import prepare_api_key
from restroom.utils import get_val
from restroom.models import APIKey


def test_get_val_for_decimal():
    "Decimals are serialized correctly"
    DecimalModel.objects.all().delete()
    _obj = DecimalModel.objects.create(value=234.45)
    obj = DecimalModel.objects.get(id=_obj.id)
    val = get_val(obj, 'value')
    expect(val).to.equal(234.45)


@scenario(prepare_api_key)
def test_get_val_for_model_instances(context):
    "Model instances are serialized correctly (returns the id)"
    obj = APIKey.objects.get(id=context.api_key.id)
    val = get_val(obj, 'user')
    expect(val).to.equal(context.user.id)


def test_get_val_for_arbitrary_objects():
    "unserializable objects returns nice error message"
    class SomeObj(object):
        def __init__(self, blah, blop):
            self.blah = blah
            self.blop = blop

        def __str__(self):
            return "Nice string representation of this crazy object"

    class Obj(object):
        def __init__(self, stuff):
            self.stuff = stuff

    some_obj = SomeObj(True, 'hahahaha')
    obj = Obj(stuff=some_obj)
    val = get_val(obj, 'stuff')
    expect(val).to.equal(
        'Could not serialize Nice string representation of this crazy object')
