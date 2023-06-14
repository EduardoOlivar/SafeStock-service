from rest_framework.filters import SearchFilter
from api.serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from api.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, logout
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import *
from rest_framework.permissions import IsAuthenticated
from django.db import connections
from django.db.models import Q
from api.pagination import SmallMediumPagination

# Create your views here.

@api_view(['GET'])
def server_status(request):
    try:
        connections['default'].cursor()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'status': 'error', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


"""Controladores de user"""


class UserListCreate(generics.ListCreateAPIView):
    queryset = Users.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination

class UsersDetail(generics.RetrieveUpdateAPIView):
    queryset = Users.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination

class UserProfileView(APIView):
    renderer_classes = [UserRenderer, ]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user  # Obtener el usuario autenticado

        serializer = ProfileUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user_id': user.pk}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValidateAccountView(APIView):
    def post(self, request, pk):
        token = request.query_params.get('token')
        user = get_object_or_404(Users, pk=pk)
        print(token)
        if token == user.token:  # Comparar el token de la solicitud con el token guardado en el usuario
            user.is_validated = True
            user.save()
            return Response({'detail': 'La cuenta ha sido validada exitosamente.'})

        return Response({'detail': 'El token de validación es inválido.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    #permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user: Users = request.user
        user.set_password(serializer.data.get('password'))
        user.save()
        return Response({'message': 'success'}, status=200)


class LoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None and user.is_validated:  #verifica que el usuario esté validado
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Inicio de sesión exitoso'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'error_de_campo': ['Email o contraseña inválidos o la cuenta no está validada']}},
                            status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):

    def post(self, request):
        logout(request)  # Cierra la sesión del usuario
        return Response({'msg': 'Se cerro la sesión con éxito'},
                        status=status.HTTP_200_OK)  # Retorna un mensaje de éxito en la respuesta

class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Link para reiniciar contraseña enviado'}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Cambio de contraseña exitoso'}, status=status.HTTP_200_OK)


"""Demas controladores"""


class ShopListCreate(generics.ListCreateAPIView):
    queryset = Shop.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class ShopDetail(generics.RetrieveUpdateAPIView):
    queryset = Shop.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class ReportSettingList(generics.ListAPIView):
    queryset = ReportSettings.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ReportSettingsSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class ReportSettingDetail(generics.RetrieveUpdateAPIView):
    queryset = ReportSettings.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ReportSettingsSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class RecommendationsList(generics.ListAPIView):
    queryset = Recommendations.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = RecommendationsSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class RecommendationsDetail(generics.RetrieveUpdateAPIView):
    queryset = Recommendations.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = RecommendationsSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class NotificationList(generics.ListAPIView):
    queryset = Notification.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = NotificationSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class NotificationDetail(generics.RetrieveUpdateAPIView):
    queryset = Notification.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = NotificationSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class UserNotificationDetail(generics.RetrieveUpdateAPIView):
    queryset = UserNotification.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserNotificationSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


# Vista para listar y crear finanzas de usuario.
class ShopFinancesListCreate(generics.ListCreateAPIView):
    queryset = ShopFinances.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopFinancesSerializer
    filter_backends = [SearchFilter,DjangoFilterBackend]
    filterset_fields = ['shop_id', 'type', 'total']
    search_fields = ['type', 'total']
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class ShopFinancesDetail(generics.RetrieveUpdateAPIView):
    queryset = ShopFinances.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopFinancesSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class SupplierListCreate(generics.ListCreateAPIView):
    queryset = Supplier.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = SupplierSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class SupplierDetail(generics.RetrieveUpdateAPIView):
    queryset = Supplier.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = SupplierSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


class DebtorListCreate(generics.ListCreateAPIView):
    queryset = Debtor.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = DebtorSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


#vista para el detalle de un deudor
class DebtorDetail(generics.RetrieveUpdateAPIView):
    queryset = Debtor.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = DebtorSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


#vista para crear la boleta
class BillDebtorCreateView(generics.CreateAPIView):
    serializer_class = BillDebtorSerializer
    # permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bill_debtor = serializer.save(debtors_id=request.data.get('debtors_id'))

        response_data = {
            'bill_debtor_id': bill_debtor.id
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


# View para listar y crear ítems.
class ItemListCreate(generics.ListCreateAPIView):
    queryset = Item.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ItemSerializer
    filter_backends = [SearchFilter,DjangoFilterBackend] #filtros backend para el nombre precio de compra y precio de venta\
    filterset_fields = ['shop_id']
    search_fields = ['name', 'buy_price', 'sell_price']
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


# View para obtener detalles y actualizar un ítem específico.
class ItemDetail(generics.RetrieveUpdateAPIView):
    queryset = Item.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ItemSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


# View para eliminado logico.
class SupplierRemoveListView(generics.RetrieveUpdateAPIView):
    queryset = Supplier.objects.filter(is_deleted=False)
    serializer_class = RemoveSupplierSerializer
    # permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


# View para eliminado logico.
class RemoveShopFinanceView(generics.RetrieveUpdateAPIView):
    queryset = ShopFinances.objects.filter(is_deleted=False)
    serializer_class = RemoveShopFinanceSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


# View para listar tiendas con capacidad de búsqueda.
class ShopListView(generics.ListAPIView):
    queryset = Shop.objects.filter(is_deleted=False)
    serializer_class = ShopListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']
    #pagination_class = SmallMediumPagination


# View para obtener detalles de una tienda específica.
class ShopDetailView(generics.RetrieveAPIView):
    queryset = Shop.objects.filter(is_deleted=False)
    serializer_class = ShopProfileSerializer
    #pagination_class = SmallMediumPagination


# View para eliminado logico.
class RemoveItemView(generics.RetrieveUpdateAPIView):
    queryset = Item.objects.filter(is_deleted=False)
    serializer_class = RemoveItemSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


#view para vender productos
class SellItemView(generics.UpdateAPIView):
    queryset = Item.objects.filter(is_deleted=False)
    serializer_class = SellItemSerializer
    # permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


#view para agregar items a una boleta
class SellItemDebtorBillView(generics.UpdateAPIView):
    queryset = BillDebtor.objects.all()
    serializer_class = SellItemsDebtorBill
    lookup_field = 'pk'
    # permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination



#view para pagar la deuda
class PaidBillDebtorView(generics.RetrieveUpdateAPIView):
    queryset = BillDebtor.objects.filter(is_deleted=False)
    serializer_class = PaidBillDebtorSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


#vista para eliminar un deudor
class RemoveDebtorView(generics.RetrieveUpdateAPIView):
    queryset = Debtor.objects.filter(is_deleted=False)
    serializer_class = RemoveDebtorSerializer
    #permission_classes = (IsAuthenticated,)
    #pagination_class = SmallMediumPagination


#vista para los productos de una shop
class ShopItemsView(generics.ListAPIView):
    serializer_class = ItemSerializer
    #permission_classes = (IsAuthenticated,)
    filter_backends = [SearchFilter,DjangoFilterBackend]
    filterset_fields = ['name','buy_price', 'sell_price','quantity','weight','category','creation_date','measure']
    search_fields = ['name']
    #pagination_class = SmallMediumPagination

    def get_queryset(self):
        shop_id = self.kwargs['shop_id']
        shop_exists = Shop.objects.filter(id=shop_id).exists()
        if not shop_exists:
            return None

        shop = Shop.objects.get(id=shop_id)
        return shop.item.filter(is_deleted=False)


#vista para los deudores de una shop
class ShopDebtorView(generics.ListAPIView):
    serializer_class = DebtorSerializer
    #permission_classes = (IsAuthenticated,)
    filter_backends = [SearchFilter,DjangoFilterBackend]
    filterset_fields = ['name','creation_date']
    search_fields = ['name']
    #pagination_class = SmallMediumPagination

    def get_queryset(self):
        shop_id = self.kwargs['shop_id']
        shop_exists = Shop.objects.filter(id=shop_id).exists()
        if not shop_exists:
            return None

        shop = Shop.objects.get(id=shop_id)
        return shop.debtor.filter(is_deleted=False)


#vista para los proveedores de una shop
class ShopSupplierView(generics.ListAPIView):
    serializer_class = SupplierSerializer
    #permission_classes = (IsAuthenticated,)
    filter_backends = [SearchFilter,DjangoFilterBackend]
    filterset_fields = ['name','creation_date']
    search_fields = ['name']
    #pagination_class = SmallMediumPagination

    def get_queryset(self):
        shop_id = self.kwargs['shop_id']
        shop_exists = Shop.objects.filter(id=shop_id).exists()
        if not shop_exists:
            return None

        shop = Shop.objects.get(id=shop_id)
        return shop.supplier.filter(is_deleted=False)


#vista para las finanzas de una shop
class ShopFinancesView(generics.ListAPIView):
    serializer_class = ShopFinancesSerializer
    #permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type','total','creation_date']
    #pagination_class = SmallMediumPagination

    def get_queryset(self):
        shop_id = self.kwargs['shop_id']
        shop_exists = Shop.objects.filter(id=shop_id).exists()
        if not shop_exists:
            return None

        shop = Shop.objects.get(id=shop_id)
        return shop.shopfinances.filter(is_deleted=False)
