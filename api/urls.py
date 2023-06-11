from api import views
from django.urls import path, re_path
from rest_framework_simplejwt.views import (TokenObtainPairView,)
from rest_framework_simplejwt import views as jwt_views

#endpoint restful
urlpatterns = [
    path('status', views.server_status),
    # Endpoints para usuarios
    re_path(r'^users/all/$', views.UserListCreate.as_view()),  # Endpoint para consultar listado de usuarios
    re_path(r'^user/(?P<pk>[0-9]+)/$', views.UsersDetail.as_view()),# Endpoint para consultar, actualizar o eliminar un usuario

    # Endpoints para tiendas
    re_path(r'^shops/all/$', views.ShopListCreate.as_view()),  # Endpoint para consultar listado de tiendas
    re_path(r'^shops/(?P<pk>[0-9]+)/$', views.ShopDetail.as_view()),# Endpoint para consultar, actualizar o eliminar una tienda

    # Endpoints para configuraciones de reportes
    re_path(r'^report_settings/all/$', views.ReportSettingList.as_view()),# Endpoint para consultar listado de configuraciones de reportes
    re_path(r'^report_settings/(?P<pk>[0-9]+)/$', views.ReportSettingDetail.as_view()),# Endpoint para consultar, actualizar o eliminar una configuración de reporte

    # Endpoints para recomendaciones
    re_path(r'^recommendations/all/$', views.RecommendationsList.as_view()),# Endpoint para consultar listado de recomendaciones
    re_path(r'^recommendations/(?P<pk>[0-9]+)/$', views.RecommendationsDetail.as_view()),# Endpoint para consultar, actualizar o eliminar una recomendación

    # Endpoints para notificaciones
    re_path(r'^notifications/all/$', views.NotificationList.as_view()),# Endpoint para consultar listado de notificaciones
    re_path(r'^notification/(?P<pk>[0-9]+)/$', views.NotificationDetail.as_view()),# Endpoint para consultar, actualizar o eliminar una notificación
    re_path(r'^user_notification/(?P<pk>[0-9]+)/$', views.UserNotificationDetail.as_view()),# Endpoint para consultar una notificación específica de un usuario

    # Endpoints para finanzas
    re_path(r'^user_finances/all/$', views.UserFinancesListCreate.as_view()),# Endpoint para consultar listado de finanzas de usuario
    re_path(r'^user_finances/(?P<pk>[0-9]+)/$', views.UserFinancesDetail.as_view()),# Endpoint para consultar, actualizar o eliminar una finanza de usuario

    # Endpoints para proveedores
    re_path(r'^suppliers/all/$', views.SupplierListCreate.as_view()),# Endpoint para consultar listado de proveedores
    re_path(r'^suppliers/(?P<pk>[0-9]+)/$', views.SupplierDetail.as_view()),# Endpoint para consultar, actualizar o eliminar un proveedor

    # Endpoints para deudores
    re_path(r'^debtors/all/$', views.DebtorListCreate.as_view()),# Endpoint para consultar listado de deudores
    re_path(r'^debtors/(?P<pk>[0-9]+)/$', views.DebtorDetail.as_view()),# Endpoint para consultar, actualizar o eliminar un deudor

    # Endpoints para productos
    re_path(r'^items/all/$', views.ItemListCreate.as_view()),# Endpoint para consultar listado de productos
    re_path(r'^items/(?P<pk>[0-9]+)/$', views.ItemDetail.as_view()),# Endpoint para consultar, actualizar o eliminar un producto


    # Endpoints para ítems de deudor de usuario
    re_path(r'^debtor_items/all/$', views.DebtorItemSoldListCreate.as_view()),# Endpoint para consultar y crear ítems de deudor de usuario
    re_path(r'^debtor_items/(?P<pk>[0-9]+)/$', views.DebtorItemSoldDetail.as_view()),# Endpoint para consultar, actualizar o eliminar un ítem de deudor de usuario

    # Endpoints para eliminar proveedor, finanza, producto, deuda, deudor
    re_path(r'^remove_supplier/(?P<pk>[0-9]+)/$', views.SupplierRemoveListView.as_view()),# Endpoint para eliminar un proveedor
    re_path(r'^remove_finance/(?P<pk>[0-9]+)/$', views.RemoveUserFinanceView.as_view()),# Endpoint para eliminar una finanza de usuario
    re_path(r'^remove_item/(?P<pk>[0-9]+)/$', views.RemoveItemView.as_view()),# Endpoint para eliminar un producto
    re_path(r'^remove_debtor_user_item/(?P<pk>[0-9]+)/$', views.RemoveUserDebtorItemsView.as_view()),# Endpoint para eliminar una deuda (pagar)
    re_path(r'^remove_debtor/(?P<pk>[0-9]+)/$', views.RemoveDebtorView.as_view()),# Endpoint para eliminar una fiado(deudor)

    # Endpoints para listas de tiendas
    re_path(r'^shop_list/all/$', views.ShopListView.as_view()),  # Endpoint para consultar listado de tiendas
    re_path(r'^shop_list/(?P<pk>[0-9]+)/$', views.ShopDetailView.as_view()),# Endpoint para consultar, actualizar o eliminar una tienda

    # Endpoint para vender un ítem
    re_path(r'^sell_item/(?P<pk>[0-9]+)/$', views.SellItemView.as_view()),  # Endpoint para vender un ítem

    # Endpoint para simular venta a un fiado
    re_path(r'^sell_item_debtor/$', views.DebtorItemsCreateView.as_view()),# Endpoint para simular venta a un fiado
]


urlpatterns += [
    # Endpoint para obtener un token
    re_path(r'^api/token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Endpoint para refrescar el token
    re_path(r'^api/token-refresh/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    # Endpoint para cambiar la contraseña
    re_path(r'^api/change_password/$', views.ChangePasswordView.as_view(), name='change_password'),

    # Endpoint para ver el perfil del usuario
    re_path(r'^user/profile/$', views.UserProfileView.as_view()),

    # Endpoint para registrarse
    re_path(r'^api/sign_up/$', views.SignupView.as_view()),

    # Endpoint para validacion del registro
    re_path(r'^api/user/(?P<pk>[0-9]+)/validate/$', views.ValidateAccountView.as_view()),

    # Endpoint para iniciar sesión
    re_path(r'^api/login/$', views.LoginView.as_view()),

    #Endpoint para cerrar sesión
    re_path('api/logout/', views.LogoutView.as_view(), name='logout'),

    # Endpoint para enviar correo electrónico de restablecimiento de contraseña
    re_path(r'^api/send_reset_password_email/$', views.SendPasswordResetEmailView.as_view(), name='send_reset_password_email'),

    # Endpoint para restablecer la contraseña
    path('api/reset_password/<uid>/<token>/', views.UserPasswordResetView.as_view(), name='reset_password'),

]
