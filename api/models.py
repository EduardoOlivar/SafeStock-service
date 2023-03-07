from django.db import models
from django.contrib.auth.models import (AbstractUser)

# Create your models here.

common_args = {'null': True, 'blank': True} #atributos generales


class GenericAttributes(models.Model):
    created = models.DateTimeField(**common_args, auto_now_add=True, editable=False)  # para saber cuando fue creado el dato
    updated = models.DateTimeField(**common_args, auto_now=True) # para saber cuando se actualizo el dato
    is_deleted = models.BooleanField(**common_args, default=False) #para un borrado logico de las vistas no borrado fisico de la bd

    class Meta:
        abstract = True


class Users(AbstractUser, GenericAttributes):
    name = models.TextField(**common_args)
    image_file = models.FileField(upload_to='user/images/', **common_args)
    phone_number = models.TextField(**common_args)
    token = models.TextField(**common_args)
    last_session = models.DateTimeField(**common_args)
    is_validated = models.BooleanField(default=False)

    @property
    def is_admin(self, user):
        return user.is_superuser

    def __str__(self):
        return self.email


class ReportSettings(GenericAttributes):
    users = models.ForeignKey(Users, on_delete=models.CASCADE, **common_args)
    is_enabled = models.BooleanField(default=False)
    period = models.IntegerField(**common_args) #atributo para que el usuario elija cada cuanto tiempo quiere el reporte


class Recommendations(GenericAttributes):
    users = models.ForeignKey(Users, on_delete=models.CASCADE, **common_args)
    is_enabled = models.BooleanField(default=False)
    period = models.IntegerField(**common_args) #atributo para que el usuario elija cada cuanto tiempo quiere las recomendaciones


class Notification(GenericAttributes):
    users = models.ManyToManyField(Users, blank=True, through='UserNotification', related_name='notification')
    is_enabled = models.BooleanField(default=False)
    period = models.IntegerField(**common_args) #atributo para que el usuario elija cada cuanto tiempo quiere las notificaciones


class UserNotification(GenericAttributes):
    users = models.ForeignKey(Users, on_delete=models.CASCADE, **common_args)
    notifications = models.ForeignKey(Notification, on_delete=models.CASCADE, **common_args)
    details = models.TextField(**common_args)


class Finance(GenericAttributes):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, **common_args, related_name='finance')
    users_finance = models.ManyToManyField(Users, blank=True, through='UserFinances', related_name='financesusers')
    period = models.IntegerField(**common_args) #atributo para que el usuario elija cada cuanto tiempo quiere las notificaciones de su finanzas
    max_spend = models.IntegerField(**common_args, default=0)


class UserFinances(GenericAttributes):
    finances = models.ForeignKey(Finance, on_delete=models.CASCADE, **common_args, related_name='userfinances')
    users = models.ForeignKey(Users, on_delete=models.CASCADE, **common_args, related_name='userfinances')
    type = models.TextField(**common_args)
    details = models.TextField(**common_args)
    total = models.FloatField(**common_args)


class Supplier(GenericAttributes):
    name = models.TextField(**common_args)
    phone_number = models.TextField(**common_args)
    details = models.TextField(**common_args)


class UserSuppliers(GenericAttributes):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, **common_args, related_name='usersuppliers')
    users = models.ForeignKey(Users, on_delete=models.CASCADE, **common_args, related_name='usersuppliers')


class Debtor(GenericAttributes):
    name = models.TextField(**common_args)
    details = models.TextField(**common_args)


class Shop(GenericAttributes):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, **common_args, related_name='user')
    name = models.TextField(**common_args)
    image_file = models.FileField(upload_to='shop/images/', **common_args)
    city = models.TextField(**common_args)
    commune = models.TextField(**common_args)
    address = models.TextField(**common_args)
    shop_type = models.TextField(**common_args)
    open_days = models.DateField(**common_args)
    opens_at = models.DateTimeField(**common_args)
    close_at = models.DateTimeField(**common_args)


class Category(GenericAttributes):
    name = models.TextField(**common_args)


class Item(GenericAttributes):
    categories = models.ForeignKey(Category, on_delete=models.CASCADE, **common_args, related_name='item')
    name = models.TextField(**common_args)
    buy_price = models.IntegerField(**common_args)
    sell_price = models.IntegerField(**common_args)
    details = models.TextField(**common_args)
    quantity = models.FloatField(**common_args)
    weight = models.FloatField(**common_args)


class ShopItems(GenericAttributes):
    shops = models.ForeignKey(Shop, on_delete=models.CASCADE, **common_args, related_name='shopitems')
    item = models.OneToOneField(Item, on_delete=models.CASCADE, **common_args, related_name='shopitems')


class UserDebtorItems(GenericAttributes):
    debtors = models.ForeignKey(Debtor, on_delete=models.CASCADE, **common_args, related_name='interdebtors')
    users = models.ForeignKey(Users, on_delete=models.CASCADE, **common_args, related_name='interusers')
    items = models.ForeignKey(Item, on_delete=models.CASCADE, **common_args, related_name='interitems')
    quantity = models.FloatField(**common_args)
    weight = models.FloatField(**common_args)
    total = models.FloatField(**common_args)
    is_paid = models.BooleanField(default=False)


