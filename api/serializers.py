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
        message = f'Gracias por confiar en SafeStock {user.email} ,\n\nHaz clic en el siguiente enlace para validar tu cuenta:\n\nhttp://localhost:3000/validate/?id={user.id}&token={token}'
        from_email = 'sender@example.com'
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)




#serializador para cambiar password dentro del perfil de usuario
class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, required=True)
    password2 = serializers.CharField(max_length=255, required=True)

    def validate(self, attrs): #metodo para validar las password al momento de cambiarlas
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user') #obtiene al usuario a traves del token
        if password != password2: #verifica que las password coincidan
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
            link = 'http://localhost:3000/recover/user?uid='+uid+'&token='+token # link generado
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


    # Serializador para UserFinances
class ShopFinancesSerializer(serializers.ModelSerializer):
    creation_date = serializers.SerializerMethodField()

    def get_creation_date(self, instance):
        return int(instance.creation_date.timestamp())
    class Meta:
        model = ShopFinances
        exclude = ['last_update','is_deleted']


    # Serializador para Supplier
class SupplierSerializer(serializers.ModelSerializer):
    creation_date = serializers.SerializerMethodField()

    def get_creation_date(self, instance):
        return int(instance.creation_date.timestamp())

    class Meta:
        model = Supplier
        exclude = ['last_update','is_deleted']


    # Serializador para Debtor
class DebtorSerializer(serializers.ModelSerializer):
    creation_date = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=255,required=True)
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.filter(is_deleted=False))

    def get_creation_date(self, instance):
        return int(instance.creation_date.timestamp())

    class Meta:
        model = Debtor
        exclude = ['last_update','is_deleted']


    def create(self, validated_data):
        shop = validated_data.pop('shop')
        print(shop)
        shop_id = shop.id
        debtor = Debtor.objects.create(shop_id=shop_id, **validated_data)
        return debtor

# Serializador para Item
class ItemSerializer(serializers.ModelSerializer):
    creation_date = serializers.SerializerMethodField()

    def get_creation_date(self, instance):
        return int(instance.creation_date.timestamp())
    class Meta:
        model = Item
        exclude = ['last_update','is_deleted','item_sold']


#serializador de boleta
class BillDebtorSerializer(serializers.ModelSerializer):
    debtors_id = serializers.PrimaryKeyRelatedField(queryset=Debtor.objects.filter(is_deleted=False))
    creation_date = serializers.SerializerMethodField()

    def get_creation_date(self, instance):
        return int(instance.creation_date.timestamp())

    class Meta:
        model = BillDebtor
        exclude = ['last_update', 'is_deleted']

    def create(self, validated_data):
        debtor_id = validated_data.pop('debtors_id')
        debtor = Debtor.objects.get(id=debtor_id)
        bill_debtor = BillDebtor.objects.create(debtors_id=debtor, **validated_data)
        return bill_debtor

#serializador de boleta
class BillDebtorRepliceSerializer(serializers.ModelSerializer):
    creation_date = serializers.SerializerMethodField()

    def get_creation_date(self, instance):
        return int(instance.creation_date.timestamp())

    class Meta:
        model = BillDebtor
        exclude = ['last_update', 'is_deleted','items']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['name'] = instance.debtors_id.name
        return data


#serializador para mostrar la cantidad de items de la boleta
class BillItemSerializer(serializers.ModelSerializer):
    def get_creation_date(self, time):
        return int(time.timestamp())

    class Meta:
        model = BillItem
        exclude = [*generic_fields,'items_id','bill_id']

    def to_representation(self, instance:BillItem):
        data = super().to_representation(instance)
        data['created_date_bill'] = self.get_creation_date(instance.bill_id.creation_date)
        data['total_bill'] = instance.bill_id.total_bill
        data['name_item'] = instance.items_id.name
        data['measure'] = instance.items_id.measure
        return data


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
class RemoveShopFinanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopFinances
        exclude = [*generic_fields]

    def update(self, instance, validated_data):
        instance.is_deleted = True #dato para eliminar de manera logica
        instance.save()
        return instance


#serializador para listar las tienda cuando no se este logueado en la app
class ShopListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id','name', 'image_file', 'address']


#serializador para el perfil de la tienda
class ShopProfileSerializer(serializers.ModelSerializer):
    items = ItemSerializer(read_only=True, many=True)

    class Meta:
        model = Shop
        fields = ['name', 'image_file', 'address', 'open_days', 'opens_at', 'close_at', 'items'] #atributos de la tabla

    def to_representation(self, instance: Shop): #atributos extra de otras tablas
        data = super().to_representation(instance)
        data['username'] = instance.user_id.username
        data['phone_number'] = instance.user_id.phone_number
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
        exclude = [*generic_fields, 'item_sold']

    def update(self, instance:Item, validated_data):
        request = self.context.get('request')
        quantity_sold = validated_data.get('quantity')
        weight_sold = validated_data.get('weight')
        shop_id = validated_data.get('shop_id')

        if instance.measure == 'unit':
            if quantity_sold <= 0: # Validar que la cantidad vendida sea mayor que cero
                raise serializers.ValidationError('La cantidad vendida debe ser mayor que cero.')
            if quantity_sold > instance.quantity:# Validar si hay suficiente stock disponible para realizar la venta
                raise serializers.ValidationError('No hay suficiente stock disponible para realizar la venta.')
            sold_price = quantity_sold * instance.sell_price
            # Crea un nuevo registro en ShopItems para la venta por cantidad
            shop_item = ShopItemSold.objects.create(
                shop_id=shop_id,
                item_id=instance,
                total_sold=sold_price,
                quantity_sold=quantity_sold,
                weight_sold=0  # No se considera el peso vendido en caso de venta por cantidad
            )
            instance.quantity -= quantity_sold
            instance.save()

        elif instance.measure == 'gram':
            if weight_sold <= 0: #Valida que el peso vendido sea mayor que cero
                raise serializers.ValidationError('El peso vendido debe ser mayor que cero.')
            if weight_sold > instance.weight:# Validar si hay suficiente peso disponible para realizar la venta
                raise serializers.ValidationError('No hay suficiente peso disponible para realizar la venta.')
            # Crea un nuevo registro en ShopItems para la venta por peso
            sold_price = (weight_sold/1000) * instance.sell_price # total de la venta
            shop_item = ShopItemSold.objects.create(
                shop_id=shop_id,
                item_id=instance,
                total_sold=round(sold_price),
                quantity_sold=0,  # No se considera la cantidad vendida en caso de venta por peso
                weight_sold=weight_sold
            )
            instance.weight -= weight_sold
            instance.save()
        return instance


#serializador para la lista de objetos
class SellItemListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity_sold = serializers.IntegerField(default=0)
    weight_sold = serializers.IntegerField(default=0)


    # serializador para asignar items a una boleta
class SellItemsDebtorBill(serializers.ModelSerializer):
    items = SellItemListSerializer(many=True)

    class Meta:
        model = BillDebtor
        exclude = [*generic_fields]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('items', None)
        return representation

    def update(self, instance, validated_data):

        try:
            items_data = validated_data['items']

            for item_data in items_data:
                current_price = 0
                item_id = item_data['id']
                quantity_sold = item_data['quantity_sold']
                weight_sold = item_data['weight_sold']
                item = Item.objects.get(pk=item_id)



                if item.measure == 'unit':
                    if quantity_sold <= 0:
                        raise serializers.ValidationError('La cantidad vendida debe ser mayor que cero.')
                    if quantity_sold > item.quantity:
                        raise serializers.ValidationError('No hay suficiente stock disponible para realizar la venta.')

                    current_price += quantity_sold * item.sell_price

                    BillItem.objects.create(
                        bill_id=instance,
                        items_id=item,
                        quantity_debtor=quantity_sold,
                        weight_debtor=0,
                        current_price=current_price
                    )

                    item.quantity -= quantity_sold
                    item.save()

                elif item.measure == 'gram':
                    if weight_sold <= 0:
                        raise serializers.ValidationError('El peso vendido debe ser mayor que cero.')
                    if weight_sold > item.weight:
                        raise serializers.ValidationError('No hay suficiente peso disponible para realizar la venta.')

                    current_price += (weight_sold / 1000) * item.sell_price

                    BillItem.objects.create(
                        bill_id=instance,
                        items_id=item,
                        quantity_debtor=0,
                        weight_debtor=weight_sold,
                        current_price=current_price
                    )

                    item.weight -= weight_sold
                    item.save()
                instance.total_bill += current_price

            instance.save()
            return instance
        except instance.DoesNotExist as e:
            return e



#serializador para el pago de manera logica una deuda
class PaidBillDebtorSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillDebtor
        exclude = [*generic_fields,'items']

    def update(self, instance, validated_data):
        instance.is_paid = True #dato para simular el pago de manera logica
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

