from api.serializers import *
from rest_framework import generics
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from api.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, logout
from rest_framework import status
from rest_framework.response import Response
from api.models import *
from rest_framework.permissions import IsAuthenticated
# Create your views here.


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
    permission_classes = (IsAuthenticated,)


class UsersDetail(generics.RetrieveUpdateAPIView):
    queryset = Users.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class UserProfileView(APIView):
    renderer_classes = [UserRenderer,]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignUpView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user: Users = request.user
        user.set_password(serializer.data.get('new_password'))
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
        print(user)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Inicio de sesión exitoso','status': 'ok'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {'error_de_campo': ['Email o contraseña invalidos']}},
                            status=status.HTTP_404_NOT_FOUND)


class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Link para reiniciar contraseña enviado'}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid,'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Cambio de contraseña exitoso'}, status=status.HTTP_200_OK)




"""Demas controladores"""


class ShopListCreate(generics.ListCreateAPIView):
    queryset = Shop.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)


class ShopDetail(generics.RetrieveUpdateAPIView):
    queryset = Shop.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)


class ReportSettingList(generics.ListAPIView):
    queryset = ReportSettings.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ReportSettingsSerializer
    permission_classes = (IsAuthenticated,)


class ReportSettingDetail(generics.RetrieveUpdateAPIView):
    queryset = ReportSettings.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ReportSettingsSerializer
    permission_classes = (IsAuthenticated,)


class RecommendationsList(generics.ListAPIView):
    queryset = Recommendations.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = RecommendationsSerializer
    permission_classes = (IsAuthenticated,)


class RecommendationsDetail(generics.RetrieveUpdateAPIView):
    queryset = Recommendations.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = RecommendationsSerializer
    permission_classes = (IsAuthenticated,)


class NotificationList(generics.ListAPIView):
    queryset = Notification.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)


class NotificationDetail(generics.RetrieveUpdateAPIView):
    queryset = Notification.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)


class UserNotificationDetail(generics.RetrieveUpdateAPIView):
    queryset = UserNotification.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserNotificationSerializer
    permission_classes = (IsAuthenticated,)


class FinancesListCreate(generics.ListCreateAPIView):
    queryset = Finance.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)


class FinancesDetail(generics.RetrieveUpdateAPIView):
    queryset = Finance.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = FinanceSerializer
    permission_classes = (IsAuthenticated,)


class UserFinancesListCreate(generics.ListCreateAPIView):
    queryset = UserFinances.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserFinancesSerializer
    permission_classes = (IsAuthenticated,)


class UserFinancesDetail(generics.RetrieveUpdateAPIView):
    queryset = UserFinances.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserFinancesSerializer
    permission_classes = (IsAuthenticated,)


class SupplierListCreate(generics.ListCreateAPIView):
    queryset = Supplier.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = SupplierSerializer
    permission_classes = (IsAuthenticated,)


class SupplierDetail(generics.RetrieveUpdateAPIView):
    queryset = Supplier.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = SupplierSerializer
    permission_classes = (IsAuthenticated,)


class UserSuppliersCreate(generics.CreateAPIView):
    queryset = UserSuppliers.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserSuppliersSerializer
    permission_classes = (IsAuthenticated,)


class UserSuppliersDetail(generics.RetrieveUpdateAPIView):
    queryset = UserSuppliers.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserSuppliersSerializer
    permission_classes = (IsAuthenticated,)


class DebtorListCreate(generics.ListCreateAPIView):
    queryset = Debtor.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = DebtorSerializer
    permission_classes = (IsAuthenticated,)


class DebtorDetail(generics.RetrieveUpdateAPIView):
    queryset = Debtor.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = DebtorSerializer
    permission_classes = (IsAuthenticated,)


class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


class CategoryDetail(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)


class ItemListCreate(generics.ListCreateAPIView):
    queryset = Item.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ItemSerializer
    permission_classes = (IsAuthenticated,)


class ItemDetail(generics.RetrieveUpdateAPIView):
    queryset = Item.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ItemSerializer
    permission_classes = (IsAuthenticated,)


class ShopItemsListCreate(generics.ListCreateAPIView):
    queryset = ShopItems.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopItemsSerializer
    permission_classes = (IsAuthenticated,)


class ShopItemsDetail(generics.RetrieveUpdateAPIView):
    queryset = ShopItems.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = ShopItemsSerializer
    permission_classes = (IsAuthenticated,)


class UserDebtorItemsListCreate(generics.ListCreateAPIView):
    queryset = UserDebtorItems.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserDebtorItemsSerializer
    permission_classes = (IsAuthenticated,)


class UserDebtorItemsDetail(generics.RetrieveUpdateAPIView):
    queryset = UserDebtorItems.objects.filter(is_deleted=False).order_by('pk')
    serializer_class = UserDebtorItemsSerializer
    permission_classes = (IsAuthenticated,)


