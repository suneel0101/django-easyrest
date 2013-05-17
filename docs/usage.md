from restroom.core import API
from expense.models import Expense

api = API()

class ExpenseResource(APIResource):
    model = Expense
    results_per_page = 50

    def serialize(self, expense):
        return {
            "shit": expense.shit,
            "id": expense.id,
            "amount": expense.amount,
            "status": expense.special_property,
        }

api.register(ExpenseResource)

class MyAPIResource(APIResource):
   def authorize(self, request):
       if request.user.is_authenticated():
           return request.user
       key = request.GET.get('apikey')
       try:
           return APIKey.objects.get(key=key).user
       except APIKey.DoesNotExist:
           return


class ExpenseResource(MyAPIResource):
    model = Expense
    results_per_page = 20
    needs_authorization = True
    filter_by_user = 'user'

    def serialize(self, expense):
        return {
            "shit": expense.shit,
            "id": expense.id,
            "amount": expense.amount,
            "status": expense.special_property,
        }

   def get_queryset(self):
       return Expense.objects.filter(status__gte=9, is_active=True)

   def search(self, params):
       filter_dict = {}
       if params.get("city"):
           filter_dict["city__slug"] = params["city"]

       if params.get("reimbursed"):
           filter_dict["status"] = 10
       qs = self.get_queryset().filter(**filter_dict)
       if params.get("order"):
          qs = qs.order_by(params["order"])
       return qs

api.register(Expense)

