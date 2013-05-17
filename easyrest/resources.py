class APIResource(object):
    model = None
    results_per_page = None
    user_field_to_restrict_by = None
    needs_authorization = False
    name = None

    def serialize(self, instance):
        raise NotImplementedError

    def authorize(self, request):
        pass

    def get_queryset(self, get_params):
        return self.model.objects.all()

    def get_list(self, get_params, user=None):
        qs = self.get_queryset(get_params)
        # Restrict by user if `user_field_to_restrict_by` is specified
        qs = (self.filter_by_user(qs, user)
              if (user and self.user_field_to_restrict_by) else qs)
        qs = self.paginate(qs, get_params.get('page'))
        return {"items": [self.serialize(obj) for obj in qs.iterator()]}

    def get_one(self, get_params, _id, user=None):
        # Try to find the object
        try:
            item = self.model.objects.get(id=_id)
        except self.model.DoesNotExist:
            return {'error': 'No result matches id: {}'.format(_id)}

        # If this resource is restricted by user
        # Make sure that user has access to the object with this _id
        # So check that there is an object with this _id that is owned by
        # `user`
        if (self.user_field_to_restrict_by and
            not (self.filter_by_user(self.get_queryset(get_params), user)
                 .filter(pk=_id)
                 .exists())):
            return {"error": "You do not have access to this data"}
        return self.serialize(item)

    def paginate(self, qs, page):
        page = int(page or 1)
        if self.results_per_page is None:
            return qs
        start = (page - 1) * self.results_per_page
        finish = page * self.results_per_page
        return qs[start:finish]

    def filter_by_user(self, qs, user):
        return qs.filter(**{self.user_field_to_restrict_by: user.id})

    @property
    def _name(self):
        return self.name or self.model.meta.db_table
