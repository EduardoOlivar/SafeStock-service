from rest_framework import serializers
from api.models import *
from backend.settings import TASK_UPLOAD_FILE_TYPES, TASK_UPLOAD_FILE_MAX_SIZE, TASK_UPLOAD_FILE_EXTENSIONS
import magic
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from backend.settings import EMAIL_HOST_USER
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail, get_connection
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError


generic_fields = ['creation_date', 'last_update', 'is_deleted']


"""Serializadores para mostrar datos de usuario"""


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        exclude = [*generic_fields]

#funcion para validar el formato de la imagen
    @staticmethod
    def validate_image_file(value):
        if value is None:
            return value
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in TASK_UPLOAD_FILE_EXTENSIONS:
            raise serializers.ValidationError("Extensión de imagen no soportada. Solo se aceptan jpeg, jpg y png")
        magic_file = magic.Magic(mime=True)
        content_type = magic_file.from_buffer(value.read())
        if content_type not in TASK_UPLOAD_FILE_TYPES:
            raise serializers.ValidationError("Tipo de imagen no soportado. Solo se aceptan jpeg, jpg y png")
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
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in TASK_UPLOAD_FILE_EXTENSIONS:
            raise serializers.ValidationError("Extensión de imagen no soportada. Solo se aceptan jpeg, jpg y png")
        magic_file = magic.Magic(mime=True)
        content_type = magic_file.from_buffer(value.read())
        if content_type not in TASK_UPLOAD_FILE_TYPES:
            raise serializers.ValidationError("Tipo de imagen no soportado. Solo se aceptan jpeg, jpg y png")
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


#serializador para registrarse
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

#serializador para cambiar password dentro del perfil de usuario
class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        password = attrs.get('password')
        new_password = attrs.get('new_password')
        user = self.context.get('user')
        if password != new_password:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        user.set_password(password)
        user.save()
        return attrs

#serializador para enviar link al correo que este autorizado
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        if Users.objects.filter(email=email).exists():
            user = Users.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/api/user/reset/'+uid+'/'+token
            subject = 'Reinicia tu contraseña'
            message = f'Presiona el siguiente link para reiniciar tu contraseña: {link}/'
            from_email = EMAIL_HOST_USER
            recipient_list = [email]
            connection = get_connection() #obtiene la conexion
            connection.open()
            send_mail(subject, message, from_email, recipient_list) #envia el email
            connection.close() #cierra la conexion
            return attrs
        else:
            raise serializers.ValidationError('No eres un usuario registrado')


#serializador para cambiar la password, aqui se verifican que coincidan,
# solo se puede acceder a este serializador luego de que se enviaran las credenciales al email
class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Las contraseñas no coinciden")
            id = smart_str(urlsafe_base64_decode(uid))
            user = Users.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('El token no es valido o expiro')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('El token no es valido o expiro')





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
