from .models import Item, UserItem
from .myauth import MyAuthenticatedResource
from easyrest.resources import APIResource
from easyrest.core import API

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


class SearchableItemResource(APIResource):
    model = Item
    name = 'searchable_item'

    def serialize(self, item):
        return {
            'id': item.id,
            'text': item.text,
            'popularity': item.popularity,
        }

    def search(self, get_params):
        """
        Some custom search logic.
        You always have access to the request.GET params
        through `get_params`
        """
        filter_kwargs = {}
        if get_params.get("popular"):
            filter_kwargs["status__gte"] = 9

        if get_params.get("contains"):
            filter_kwargs["text__icontains"] = get_params["contains"]
        return {"items": [
            self.serialize(obj)
            for obj in self.get_queryset().filter(**filter_kwargs)]}


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
api.register(SearchableItemResource)
api.register(ReverseOrderItemResource)
api.register(AuthorizedItemResource)
api.register(AuthorizedItemResourceByUser)
