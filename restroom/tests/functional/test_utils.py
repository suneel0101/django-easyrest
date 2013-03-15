from sure import expect
from restroom.tests.models import DecimalModel
from restroom.utils import get_val


def test_get_val_for_decimal():
    DecimalModel.objects.all().delete()
    _obj = DecimalModel.objects.create(value=234.45)
    obj = DecimalModel.objects.get(id=_obj.id)
    field = [f for f in DecimalModel._meta.fields if f.attname == 'value'][0]
    val = get_val(obj, 'value', field)
    expect(val).to.equal(234.45)
