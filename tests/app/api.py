from .models import Item
from restroom.resources import APIResource
from restroom.core import API

api = API()


class ItemResource(APIResource):
    model = Item
    name = 'item'

    def serialize(self, item):
        return {
            'id': item.id,
            'text': item.text,
            'popularity': item.popularity,
        }


class ReverseOrderItemResource(APIResource):
    model = Item
    name = 'reverse_order_item'

    def get_queryset(self):
        return Item.objects.order_by('-id')

    def serialize(self, item):
        return {
            'id': item.id,
            'text': item.text,
            'popularity': item.popularity,
        }


class PaginatedItemResource(APIResource):
    model = Item
    name = 'paginated_item'
    results_per_page = 20

    def serialize(self, item):
        return {
            'id': item.id,
            'text': item.text,
            'popularity': item.popularity,
        }

api.register(ItemResource)
api.register(PaginatedItemResource)
api.register(ReverseOrderItemResource)
