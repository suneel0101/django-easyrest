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


class ExpenseResource(APIResource):
    model = Expense
    results_per_page = 20

    needs_authentication = True
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

   def authorize(self, request):
       pass

api.register(Expense)

