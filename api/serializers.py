from rest_framework import serializers
from api.models import *
from backend.settings import TASK_UPLOAD_FILE_TYPES, TASK_UPLOAD_FILE_MAX_SIZE
import magic


generic_fields = ['creation_date', 'last_update', 'is_deleted']


"""Serializadores para mostrar datos de usuario"""


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        exclude = [*generic_fields]

    @staticmethod
    def validate_image_file(value):
        if value is None:
            return value
        magic_file = magic.Magic(mime=True)
        content_type = magic_file.from_buffer(value.read())
        if content_type not in TASK_UPLOAD_FILE_TYPES:
            raise serializers.ValidationError("Tipo de archivo no soportado. Solo se aceptan jpeg, jpg y png")
        if value.size > TASK_UPLOAD_FILE_MAX_SIZE:
            raise serializers.ValidationError(f"El tamaño debe ser menor a {TASK_UPLOAD_FILE_MAX_SIZE} bytes. El tamaño actual es {value.size} bytes")
        return value
    # ['image/jpeg','image/jpg','image/png']


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = Users
        fields = ['email', 'password']


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        exclude = [*generic_fields, "user"]

    @staticmethod
    def validate_image_file(value):
        if value is None:
            return value
        magic_file = magic.Magic(mime=True)
        content_type = magic_file.from_buffer(value.read())
        if content_type not in TASK_UPLOAD_FILE_TYPES:
            raise serializers.ValidationError("Tipo de archivo no soportado. Solo se aceptan jpeg, jpg y png")
        if value.size > TASK_UPLOAD_FILE_MAX_SIZE:
            raise serializers.ValidationError(f"El tamaño debe ser menor a {TASK_UPLOAD_FILE_MAX_SIZE} bytes. El tamaño actual es {value.size} bytes")
        return value
    # ['image/jpeg','image/jpg','image/png']


class ShopReplaceSerializer(ShopSerializer):

    class Meta:
        model = Shop
        fields = ['address', 'name']


class UserProfileSerializer(UserSerializer):
    shop = ShopReplaceSerializer()


class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = Users
        fields = ['email', 'username', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = Users(email=self.validated_data['email'], username=self.validated_data['username'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Las contraseñas deben coincidir.'})
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(max_length=255, required=True)

    class Meta:
        fields = ['password', 'new_password']

    def validate(self, attrs):
        password = attrs.get('password')
        new_password = attrs.get('new_password')
        user = self.context.get('user')
        if password != new_password:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        user.set_password(password)
        user.save()
        return attrs


"""Serializadores para las demas clases"""


class ReportSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportSettings
        exclude = [*generic_fields, 'users']


class RecommendationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recommendations
        exclude = [*generic_fields, 'users']


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        exclude = [*generic_fields, 'users']


class UserNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserNotification
        exclude = [*generic_fields, 'users']


class FinanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Finance
        exclude = [*generic_fields, 'user']


class UserFinancesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFinances
        exclude = [*generic_fields, 'users', 'finances']


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        exclude = [*generic_fields]


class UserSuppliersSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSuppliers
        exclude = [*generic_fields]


class DebtorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Debtor
        exclude = [*generic_fields]


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = [*generic_fields]


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        exclude = [*generic_fields, 'categories']


class ShopItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopItems
        exclude = [*generic_fields]


class UserDebtorItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDebtorItems
        exclude = [*generic_fields, 'users', 'debtors', 'items']
