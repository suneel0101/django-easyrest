class APIResource(object):
    model = None
    results_per_page = None
    restrict_by_user = None
    needs_authentication = False
    name = None

    def serialize(self, instance):
        raise NotImplementedError

    def authorize(self, request):
        pass

    def get_queryset(self):
        return self.model.objects.all()

    def get_list(self, user=None, page=1):
        qs = self.get_queryset()
        qs = (self.filter_by_user(qs, user)
              if (user and self.restrict_by_user) else qs)
        qs = self.paginate(qs, int(page))
        return {"items": [self.serialize(obj) for obj in qs.iterator()]}

    def get_one(self, _id, user=None):
        # Try to find the object
        try:
            item = self.model.objects.get(id=_id)
        except self.model.DoesNotExist:
            return {'error': 'No result matches id: {}'.format(_id)}

        # Make sure user is authorized for to see this item
        if (self.restrict_by_user and
            not (self.filter_by_user(self.get_queryset(), user)
                 .filter(pk=_id)
                 .exists())):
            return {"error": "You do not have access to this data"}
        return self.serialize(item)

    def paginate(self, qs, page):
        if self.results_per_page is None:
            return qs
        start = (page - 1) * self.results_per_page
        finish = page * self.results_per_page
        return qs[start:finish]

    def filter_by_user(self, qs, user):
        return qs.filter(**{self.restrict_by_user: user.id})

    @property
    def _name(self):
        return self.name or self.model.meta.db_table
