from rest_framework import serializers
from api.models import *
from backend.settings import TASK_UPLOAD_FILE_TYPES, TASK_UPLOAD_FILE_MAX_SIZE, TASK_UPLOAD_FILE_EXTENSIONS
import magic
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
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

#metodo para validar la imagen por extencion y por metadato
    @staticmethod
    def validate_image_file(value):
        if value is None:
            return value
        file_extension = value.name.split('.')[-1].lower() #deja solo la parte que esta despues del punto, ejemplo: "imagen.jpg" lo deja en "jpg"
        if file_extension not in TASK_UPLOAD_FILE_EXTENSIONS:#valida la extension
            raise serializers.ValidationError("Extensión de imagen no soportada. Solo se aceptan jpeg, jpg y png")
        magic_file = magic.Magic(mime=True) #se instancia la libreria magic
        content_type = magic_file.from_buffer(value.read()) #se abre el archivo que se esta subiendo
        if content_type not in TASK_UPLOAD_FILE_TYPES:#valida el mimetype o metadato
            raise serializers.ValidationError("Tipo de imagen no soportado. Solo se aceptan jpeg, jpg y png")
        if value.size > TASK_UPLOAD_FILE_MAX_SIZE:#valida el peso de la imagen
            raise serializers.ValidationError(f"El tamaño debe ser menor a {TASK_UPLOAD_FILE_MAX_SIZE} bytes. El tamaño actual es {value.size} bytes")
        return value


#serializador para el login del usuario donde se le pide el email y la password
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = Users
        fields = ['email', 'password']

#serializador para la tienda
class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        exclude = [*generic_fields]

    @staticmethod #metodo para validar la imagen por extencion y por metadato
    def validate_image_file(value):
        if value is None:
            return value
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in TASK_UPLOAD_FILE_EXTENSIONS: #valida la extension
            raise serializers.ValidationError("Extensión de imagen no soportada. Solo se aceptan jpeg, jpg y png")
        magic_file = magic.Magic(mime=True)
        content_type = magic_file.from_buffer(value.read())
        if content_type not in TASK_UPLOAD_FILE_TYPES: #valida el mimetype o metadato
            raise serializers.ValidationError("Tipo de imagen no soportado. Solo se aceptan jpeg, jpg y png")
        if value.size > TASK_UPLOAD_FILE_MAX_SIZE: #valida el peso de la imagen
            raise serializers.ValidationError(f"El tamaño debe ser menor a {TASK_UPLOAD_FILE_MAX_SIZE} bytes. El tamaño actual es {value.size} bytes")
        return value

#serializador para mostrar los datos del perfil de usuario
class ProfileUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = ['username', 'phone_number', 'image_file','id'] #atributos que se mostraran

    def to_representation(self, instance: Users): #metodo para poder agregar data de otras tablas haciendo joins entre tablas
        data = super().to_representation(instance)
        if hasattr(instance, 'shop'):
            data['name_shop'] = instance.shop.name
            data['address_shop'] = instance.shop.address
            data['shop_id'] = instance.shop.id
        else:
            data['name_shop'] = None
            data['address_shop'] = None
            data['shop_id'] = None
        return data


#serializador para registrarse
class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = Users
        fields = ['email', 'password', 'password2']

    def create(self, validated_data):
        password = validated_data['password']
        password2 = validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Las contraseñas deben coincidir.'})

        user = Users(email=validated_data['email'])
        user.set_password(password)
        user.save()

        # Generar y guardar el token
        token = default_token_generator.make_token(user)
        user.token = token
        user.save()

        # Enviar el correo de validación
        self.send_validation_email(user, token)

        return user

    def send_validation_email(self, user, token):
        subject = 'Validación de cuenta'
        message = f' Gracias por confiar en SafeStock {user.email} ,\n\nHaz clic en el siguiente enlace para validar tu cuenta:\n\nhttp://localhost:3000/validate?token={token}'
        from_email = 'sender@example.com'
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)




#serializador para cambiar password dentro del perfil de usuario
class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs): #metodo para validar las password al momento de cambiarlas
        password = attrs.get('password')
        new_password = attrs.get('new_password')
        user = self.context.get('user') #obtiene al usuario a traves del token
        if password != new_password: #verifica que las password coincidan
            raise serializers.ValidationError("Las contraseñas no coinciden")
        user.set_password(password)
        user.save() #metodo para guardar y encriptar la password
        return attrs

#serializador para enviar link al correo que este autorizado
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email') # se obtiene el email
        if Users.objects.filter(email=email).exists(): #se valida que el email exista y lo filtra para que solo obtenga el mail que solicito
            user = Users.objects.get(email=email) # se trae el email de la bd
            uid = urlsafe_base64_encode(force_bytes(user.id)) #encode para seguridad en el token que se le asignara al usuario
            token = PasswordResetTokenGenerator().make_token(user) # se le genera un token al usuario para mandar el email
            link = 'http://localhost:3000/api/user/reset/'+uid+'/'+token # link generado
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
            raise serializers.ValidationError('No eres un usuario registrado') # error si el usuario no se encontro en la bd


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
            uid = self.context.get('uid') # se obtiene el uid que se le genero al usuario
            token = self.context.get('token') # se obtiene el token asignado al usuario
            if password != password2: #valida las password
                raise serializers.ValidationError("Las contraseñas no coinciden")
            id = smart_str(urlsafe_base64_decode(uid))
            user = Users.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):#en caso de que no coincida el uid o el token se lanza el error
                raise serializers.ValidationError('El token no es valido o expiro')
            user.set_password(password)
            user.save() #metodo para guardar y encriptar la password
            return attrs
        except DjangoUnicodeDecodeError as identifier: #en caso de que no coincida el uid o el token se lanza el error
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('El token no es valido o expiro')





"""Serializadores para las demas clases"""


    # Serializador para ReportSettings
class ReportSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportSettings
        exclude = [*generic_fields, 'users']


    # Serializador para Recommendations
class RecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendations
        exclude = [*generic_fields, 'users']


    # Serializador para Notification
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        exclude = [*generic_fields, 'users']


    # Serializador para UserNotification
class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        exclude = [*generic_fields]


    # Serializador para Finance
class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finance
        exclude = [*generic_fields]


    # Serializador para UserFinances
class UserFinancesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFinances
        exclude = [*generic_fields]


    # Serializador para Supplier
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        exclude = [*generic_fields]


    # Serializador para Debtor
class DebtorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debtor
        exclude = [*generic_fields]


    # Serializador para Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = [*generic_fields]


# Serializador para Item
class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        exclude = [*generic_fields]


# Serializador para ShopItems
class ShopItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopItems
        exclude = [*generic_fields]


# Serializador para UserDebtorItems
class UserDebtorItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDebtorItems
        exclude = [*generic_fields]


# serializador para eliminar de manera logica un proveedor
class RemoveSupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        exclude = [*generic_fields]

    def update(self, instance, validated_data):
        instance.is_deleted = True #dato para eliminar de manera logica
        instance.save()
        return instance


#serializador para eliminar de manera logica una finanza (gasto o ganancia)
class RemoveUserFinanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserFinances
        exclude = [*generic_fields]

    def update(self, instance, validated_data):
        instance.is_deleted = True #dato para eliminar de manera logica
        instance.save()
        return instance


#serializador para listar las tienda cuando no se este logueado en la app
class ShopListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['name', 'image_file', 'address']


#serializador para el perfil de la tienda
class ShopProfileSerializer(serializers.ModelSerializer):
    items = ItemSerializer(read_only=True, many=True)

    class Meta:
        model = Shop
        fields = ['name', 'image_file', 'address', 'open_days', 'opens_at', 'close_at', 'items'] #atributos de la tabla

    def to_representation(self, instance: Shop): #atributos extra de otras tablas
        data = super().to_representation(instance)
        data['username'] = instance.user.username
        data['phone_number'] = instance.user.phone_number
        return data


#serializador para eliminar de manera logica un producto
class RemoveItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        exclude = [*generic_fields]

    def update(self, instance, validated_data):
        instance.is_deleted = True #dato para eliminar de manera logica
        instance.save()
        return instance


#serializador para simular una venta de items y guardar registro de esta en la tabla ShopItems
class SellItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        exclude = [*generic_fields]

    def update(self, instance, validated_data):
        request = self.context.get('request')
        quantity_sold = validated_data.get('quantity_sold')
        weight_sold = validated_data.get('weight_sold')

        # Verificar si se especificó tanto la cantidad vendida como el peso vendido
        if quantity_sold is not None and weight_sold is not None:
            raise serializers.ValidationError('Debes especificar la cantidad vendida o el peso vendido, no ambos.')

        if quantity_sold is not None:
            if quantity_sold <= 0: # Validar que la cantidad vendida sea mayor que cero
                raise serializers.ValidationError('La cantidad vendida debe ser mayor que cero.')
            if quantity_sold > instance.quantity:# Validar si hay suficiente stock disponible para realizar la venta
                raise serializers.ValidationError('No hay suficiente stock disponible para realizar la venta.')
            sold_price = quantity_sold * instance.sell_price
            # Crea un nuevo registro en ShopItems para la venta por cantidad
            shop_item = ShopItems.objects.create(
                shop_id=request.user.shop.id,
                item_id=instance.id,
                total_sold=sold_price,
                quantity_sold=quantity_sold,
                weight_sold=0  # No se considera el peso vendido en caso de venta por cantidad
            )
            instance.quantity -= quantity_sold
            instance.save()

        elif weight_sold is not None:
            if weight_sold <= 0: #Valida que el peso vendido sea mayor que cero
                raise serializers.ValidationError('El peso vendido debe ser mayor que cero.')
            if weight_sold > instance.weight:# Validar si hay suficiente peso disponible para realizar la venta
                raise serializers.ValidationError('No hay suficiente peso disponible para realizar la venta.')
            # Crea un nuevo registro en ShopItems para la venta por peso
            sold_price = weight_sold * instance.sell_price # total de la venta
            shop_item = ShopItems.objects.create(
                shop_id=request.user.shop.id,
                item_id=instance.id,
                total_sold=sold_price,
                quantity_sold=0,  # No se considera la cantidad vendida en caso de venta por peso
                weight_sold=weight_sold
            )
            instance.quantity = 0
            instance.save()
        return instance


class SellDebtorItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDebtorItems
        exclude = [*generic_fields]

    def create(self, validated_data):
        items_data = self.context['request'].data['items']
        debtor = validated_data['debtors_id']
        user = validated_data['user_id']
        debtor_items = []

        for item_data in items_data: #se recorren los productos o el producto
            item = Item.objects.get(id=item_data['id']) #se busca el producto en la bd
            quantity_debtor = item_data['quantity_debtor'] #se pasa la cantidad de un producto
            weight_debtor = item_data['weight_debtor'] #se pasa el peso de un producto
            total_debtor = quantity_debtor * item.sell_price if quantity_debtor else weight_debtor * item.sell_price #calcula el total adeudado de forma dinámica dependiendo de si se vendió por cantidad o por peso.

            if quantity_debtor and quantity_debtor > item.quantity: #validacion para el stock
                raise serializers.ValidationError('No hay suficiente stock disponible para realizar la venta del item.')

            if weight_debtor and weight_debtor > item.weight:#validacion para el stock
                raise serializers.ValidationError('No hay suficiente peso disponible para realizar la venta del item.')

            if quantity_debtor: # si es cantidad se decrementa en la tabla de item
                item.quantity -= quantity_debtor
            elif weight_debtor: # si es peso se decrementa en la tabla de item
                item.weight -= weight_debtor
            item.save() #se guarda
            #se crea una instancia para guardar los resultados en la tabla UserDebtorItems
            debtor_item = UserDebtorItems(
                debtors_id=debtor,
                user_id=user,
                items_id=item,
                quantity_debtor=quantity_debtor,
                weight_debtor=weight_debtor,
                total_debtor=total_debtor,
                is_paid=False
            )
            debtor_items.append(debtor_item)

        UserDebtorItems.objects.bulk_create(debtor_items)
        return debtor_items


#serializador para eliminar de manera logica una deuda
class RemoveUserDebtorItemsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDebtorItems
        exclude = [*generic_fields]

    def update(self, instance, validated_data):
        instance.is_deleted = True #dato para eliminar de manera logica
        instance.save()
        return instance


#serializador para eliminar de manera logica un deudor
class RemoveDebtorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Debtor
        exclude = [*generic_fields]

    def update(self, instance, validated_data):
        instance.is_deleted = True #dato para eliminar de manera logica
        instance.save()
        return instance
