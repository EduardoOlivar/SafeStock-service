from dashboard import views
from django.urls import re_path



urlpatterns = [
    re_path(r'^report_items/(?P<shop_id>[0-9]+)/$', views.ReportShopAllItemView.as_view()),
    re_path(r'^report_items/(?P<shop_id>[0-9]+)/$', views.ReportShopItemView.as_view()),
]