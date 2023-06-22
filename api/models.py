from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin

# Create your models here.

common_args = {'null': True, 'blank': True} #atributos generales


class GenericAttributes(models.Model):
    creation_date = models.DateTimeField(**common_args, auto_now_add=True, editable=False)  # para saber cuando fue creado el dato
    last_update = models.DateTimeField(**common_args, auto_now=True) # para saber cuando se actualizo el dato
    is_deleted = models.BooleanField(**common_args, default=False) #para un borrado logico de las vistas no borrado fisico de la bd

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


#tabla de usuario
class Users(AbstractBaseUser, PermissionsMixin,GenericAttributes):
    email = models.EmailField(max_length=255, unique=True, **common_args)
    username = models.TextField(**common_args)
    image_file = models.FileField(upload_to='uploads/user/images/')
    phone_number = models.TextField(**common_args)
    token = models.TextField(**common_args)
    last_session = models.DateTimeField(**common_args,auto_now_add=True)
    is_validated = models.BooleanField(**common_args,default=False)
    is_staff = models.BooleanField(**common_args,default=False)
    is_admin = models.BooleanField(**common_args, default=False)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff


#tabla para activar desactivar reportes
class ReportSettings(GenericAttributes):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, **common_args)
    is_enabled = models.BooleanField(default=False)
    period = models.IntegerField(**common_args) #atributo para que el usuario elija cada cuanto tiempo quiere el reporte


#tabla de recomendaciones
class Recommendations(GenericAttributes):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, **common_args)
    is_enabled = models.BooleanField(default=False)
    period = models.IntegerField(**common_args) #atributo para que el usuario elija cada cuanto tiempo quiere las recomendaciones


#tabla de notificaciones a los usuarios
class Notification(GenericAttributes):
    user_id = models.ManyToManyField(Users, blank=True, through='UserNotification', related_name='notification')
    is_enabled = models.BooleanField(default=False)
    period = models.IntegerField(**common_args) #atributo para que el usuario elija cada cuanto tiempo quiere las notificaciones


class UserNotification(GenericAttributes):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE, **common_args)
    notification_id = models.ForeignKey(Notification, on_delete=models.CASCADE, **common_args)
    details = models.TextField(**common_args)


#tabla para el negocio
class Shop(GenericAttributes):
    AVAILABLE_SHOP_TYPE = [
        ('negocio_pequeño', 'Negocio de Barrio'),
        ('panaderia', 'Panaderia'),
        ('verduleria', 'Verduleria'),
        ('carniceria', 'Carniceria'),
        ('mini_market', 'MiniMarket')
    ]
    user_id = models.OneToOneField(Users, on_delete=models.CASCADE, **common_args, related_name='shop')
    name = models.TextField(**common_args)
    image_file = models.FileField(upload_to='uploads/shop/images/', **common_args)
    address = models.TextField(**common_args)
    shop_type = models.TextField(**common_args, choices=AVAILABLE_SHOP_TYPE, default='negocio_pequeño')
    open_days = models.IntegerField(**common_args)
    opens_at = models.TimeField(**common_args)
    close_at = models.TimeField(**common_args)


#tabla para el registro si es una ganancia o es un gasto
class ShopFinances(GenericAttributes):
    AVAILABLE_FINANCE_TYPE = [
        ('profit', 'Ganancia'),
        ('cost', 'Gasto')
    ]
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE, **common_args, related_name='shopfinances')
    type = models.TextField(**common_args, choices=AVAILABLE_FINANCE_TYPE, default='profit')
    details = models.TextField(**common_args)
    total = models.IntegerField(**common_args)



#tabla para el proveedor
class Supplier(GenericAttributes):
    name = models.TextField(**common_args)
    phone_number = models.TextField(**common_args)
    details = models.TextField(**common_args)
    shop_id = models.ForeignKey(Shop, **common_args,on_delete=models.CASCADE, related_name='supplier')


#tabla del deudor
class Debtor(GenericAttributes):
    name = models.TextField(**common_args)
    details = models.TextField(**common_args)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, **common_args, related_name='debtor')


#tabla para los productos del negocio
class Item(GenericAttributes):
    AVAILABLE_CATEGORY = [
        ('lacteos', 'Lacteos'),
        ('carniceria', 'Carniceria'),
        ('panaderia', 'Panaderia'),
        ('despensa', 'Despensa'),  # aqui poner que la despensa es para arroz, fideos, etc
        ('botilleria', 'Botilleria'),
        ('frutas_verduras', 'Frutas o Verduras'),
        ('limpieza', 'Limpieza'),
        ('mascotas', 'Mascotas')
    ]

    AVAILABLE_TYPE = [
        ('unit', 'Unidad'),
        ('gram', 'Gramos')
    ]
    measure = models.TextField(**common_args, choices=AVAILABLE_TYPE, default='unit')
    category = models.TextField(**common_args, choices=AVAILABLE_CATEGORY, default='despensa')
    name = models.TextField(**common_args)
    buy_price = models.IntegerField(**common_args, default=0)
    sell_price = models.IntegerField(**common_args, default=0)
    details = models.TextField(**common_args)
    quantity = models.IntegerField(**common_args, default=0) # la catidad sera por unidad
    weight = models.IntegerField(**common_args, default=0) # peso se medira en gramos
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE, **common_args, related_name='item')
    item_sold = models.ManyToManyField(Shop, blank=True, through='ShopItemSold', related_name='item_sold')


#tabla para suponer una venta y poder tener registro de lo que se "vendio"
class ShopItemSold(GenericAttributes):
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE, **common_args, related_name='shopitemsold')
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE, **common_args, related_name='shopitemsold')
    total_sold = models.IntegerField(**common_args, default=0)  # atributo para tener un registro de la venta
    quantity_sold = models.IntegerField(**common_args, default=0) # la catidad sera por unidad
    weight_sold = models.IntegerField(**common_args, default=0) # peso se medira en gramos
    date = models.DateTimeField(**common_args, auto_now=True)


#tabla para la boleta
class BillDebtor(GenericAttributes):
    debtors_id = models.ForeignKey(Debtor, on_delete=models.CASCADE, **common_args, related_name='bill')
    total_bill = models.IntegerField(**common_args, default=0)
    is_paid = models.BooleanField(default=False)
    items = models.ManyToManyField(Item, blank=True ,through='BillItem', related_name='bills')


#tabla para guardar el registro de los items que el usuario fio
class BillItem(GenericAttributes):
    bill_id = models.ForeignKey(BillDebtor, on_delete=models.CASCADE, **common_args, related_name='billitem')
    items_id = models.ForeignKey(Item, on_delete=models.CASCADE, **common_args, related_name='billitem')
    quantity_debtor = models.IntegerField(**common_args)
    weight_debtor = models.IntegerField(**common_args)
    current_price = models.IntegerField(**common_args) #precio en el momento en que se fiaron los item



