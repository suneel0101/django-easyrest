class APIResource(object):
    model = None
    results_per_page = None
    filter_by_user_path = None
    needs_authentication = False

    def serialize(self, instance):
        raise NotImplementedError

    def authorize(self, request):
        pass

    def get_queryset(self):
        return self.model.objects.all()

    def get_list(self, user=None):
        qs = self.filter_for_user(self.get_queryset(), user)
        return {"items": [self.serialize(obj) for obj in qs.iterator()]}

    def get_one(self, _id, user=None):
        # Try to find the object
        try:
            item = self.model.objects.get(id=_id)
        except self.model.DoesNotExist:
            return {'error': 'No result matches id: {}'.format(_id)}

        # Make sure user is authorized for to see this item
        if (self.filter_by_user_field and
            user.id != self.get_user_id(item)):
            return {"error": "You do not have access to this data"}
        return self.serialize(item)

    def filter_for_user(self, qs, user):
        if user and self.filter_by_user_path:
            qs = qs.filter(**{self.filter_by_user_field: user.id})
        return qs

    def get_user_id(self, item):
        sequence = self.filter_by_user_path.split("__")
        return reduce(
            lambda x, y: getattr(x, y),
            [getattr(item, sequence[0])] + sequence[1:]).id
