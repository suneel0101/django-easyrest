from .models import Item, UserItem
from .myauth import MyAuthenticatedResource
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


class AuthorizedItemResource(MyAuthenticatedResource):
    model = UserItem
    name = 'authorized_item'
    needs_authentication = True

    def serialize(self, item):
        return {
            'name': item.name,
            'id': item.id,
            'user_id': item.user.id,
        }


class AuthorizedItemResourceByUser(MyAuthenticatedResource):
    model = UserItem
    name = 'by_user_authorized_item'
    needs_authentication = True
    restrict_by_user = 'user'

    def serialize(self, item):
        return {
            'name': item.name,
            'id': item.id,
            'user_id': item.user.id,
        }


api.register(ItemResource)
api.register(PaginatedItemResource)
api.register(ReverseOrderItemResource)
api.register(AuthorizedItemResource)
api.register(AuthorizedItemResourceByUser)
