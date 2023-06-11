from dashboard import views
from django.urls import re_path



urlpatterns = [
    #endpoint para obtener el reporte de todos los items de la shop
    re_path(r'^report_all_items/(?P<shop_id>[0-9]+)/$', views.ReportShopAllItemView.as_view()),

    #endpoint para obtener el reporte de un item de la shop
    re_path(r'^report_item/(?P<shop_id>[0-9]+)/$', views.ReportShopItemView.as_view()),
]