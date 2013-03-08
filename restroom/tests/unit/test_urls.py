# from mock import patch
# from restroom import api
# from restroom.tests.utils import assert_patterns_are_equal
# from restroom.tests.models import Modelo


# @patch('restroom.core.RestroomItemView')
# @patch('restroom.core.RestroomListView')
# def test_restroom_urls(RestroomListView, RestroomItemView):
#     "restroom.urlpatterns should equal api.get_urls()"
#     RestroomItemView.as_view.return_value = 'item view'
#     RestroomListView.as_view.return_value = 'list view'
#     api.register(Modelo)
#     from restroom.urls import urlpatterns
#     assert_patterns_are_equal(urlpatterns, api.get_urls())
#     api.resources = []
