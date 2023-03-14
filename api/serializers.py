from rest_framework import serializers
from api.models import *


generic_fields = ['created', 'updated', 'is_deleted']


"""Serializadores para mostrar datos de usuario"""


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        exclude = [*generic_fields]


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = Users
        fields = ['email', 'password']


class ShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        exclude =[*generic_fields, "user"]


class ShopRepliceSerializer(ShopSerializer):

    class Meta:
        model = Shop
        fields = ['address', 'name']


class UserProfileSerializer(UserSerializer):
    shop = ShopRepliceSerializer()


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