from api import views
from django.urls import path, re_path
from rest_framework_simplejwt.views import (TokenObtainPairView,)
from rest_framework_simplejwt import views as jwt_views

#endpoint restful
urlpatterns = [
    path('status', views.server_status),
    re_path(r'^users/all/$', views.UserListCreate.as_view()), #endpoint para consultar listado de usuarios
    re_path(r'^user/(?P<pk>[0-9]+)/$', views.UsersDetail.as_view()),# endpoint para consultar usuario especifico, eliminarlo ,recuperarlo o updatearlo
    re_path(r'^shops/all/$', views.ShopListCreate.as_view()),
    re_path(r'^shops/(?P<pk>[0-9]+)/$', views.ShopDetail.as_view()),
    re_path(r'^report_settings/all/$', views.ReportSettingList.as_view()),
    re_path(r'^report_settings/(?P<pk>[0-9]+)/$', views.ReportSettingDetail.as_view()),
    re_path(r'^recommendations/all/$', views.RecommendationsList.as_view()),
    re_path(r'^recommendations/(?P<pk>[0-9]+)/$', views.RecommendationsDetail.as_view()),
    re_path(r'^notifications/all/$', views.NotificationList.as_view()),
    re_path(r'^notification/(?P<pk>[0-9]+)/$', views.NotificationDetail.as_view()),
    re_path(r'^user_notification/(?P<pk>[0-9]+)/$', views.UserNotificationDetail.as_view()),
    re_path(r'^finances/all/$', views.FinancesListCreate.as_view()),
    re_path(r'^finances/(?P<pk>[0-9]+)/$', views.FinancesDetail.as_view()),
    re_path(r'^user_finances/all/$', views.UserFinancesListCreate.as_view()),
    re_path(r'^user_finances/(?P<pk>[0-9]+)/$', views.UserFinancesDetail.as_view()),
    re_path(r'^suppliers/all/$', views.SupplierListCreate.as_view()),
    re_path(r'^suppliers/(?P<pk>[0-9]+)/$', views.SupplierDetail.as_view()),
    re_path(r'^debtors/all/$', views.DebtorListCreate.as_view()),
    re_path(r'^debtors/(?P<pk>[0-9]+)/$', views.DebtorDetail.as_view()),
    re_path(r'^categories/all/$', views.CategoryListCreate.as_view()),
    re_path(r'^categories/(?P<pk>[0-9]+)/$', views.CategoryDetail.as_view()),
    re_path(r'^items/all/$', views.ItemListCreate.as_view()),
    re_path(r'^items/(?P<pk>[0-9]+)/$', views.ItemDetail.as_view()),
    # re_path(r'^shops_items/all/$', views.ShopItemsListCreate.as_view()),
    # re_path(r'^shops_items/(?P<pk>[0-9]+)/$', views.ShopItemsDetail.as_view()),
    re_path(r'^user_debtor_items/all/$', views.UserDebtorItemsListCreate.as_view()),
    re_path(r'^user_debtor_items/(?P<pk>[0-9]+)/$', views.UserDebtorItemsDetail.as_view()),
    re_path(r'^remove_supplier/(?P<pk>[0-9]+)/$', views.SupplierRemoveListView.as_view()),
    re_path(r'^remove_finance/(?P<pk>[0-9]+)/$', views.RemoveUserFinanceView.as_view()),
    re_path(r'^remove_item/(?P<pk>[0-9]+)/$', views.RemoveItemView.as_view()),
    re_path(r'^shop_list/all/$', views.ShopListView.as_view()),
    re_path(r'^shop_list/(?P<pk>[0-9]+)/$', views.ShopDetailView.as_view()),
]


urlpatterns += [
    re_path(r'^api/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),# endpoint para obtener un token
    re_path(r'^api/token-refresh/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),# endpoint para refresh token
    re_path(r'^api/change_password/$', views.ChangePasswordView.as_view(), name='change_password'),# endpoint para cambiar la contraseña
    re_path(r'^user/profile/$', views.UserProfileView.as_view()),  # endpoint para ver perfil de user
    re_path(r'^api/sign_up/$', views.SignUpView.as_view()),  # endpoint para registrarte
    re_path(r'^api/login/$', views.LoginView.as_view()),  # endpoint para login
    re_path(r'^api/send_reset_password_email/$', views.SendPasswordResetEmailView.as_view(), name='send_reset_password_email'),#endpoint para pedir un cambio de contraseña via mail
    path('api/reset_password/<uid>/<token>/', views.UserPasswordResetView.as_view(), name='reset_password'),#endpoint para ccambiar la contraseña si se tiene uid y el token asignado

]
