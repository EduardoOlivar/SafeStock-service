# Generated by Django 4.2.1 on 2023-06-01 01:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_rename_categories_item_categories_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='finance',
            old_name='users_finance',
            new_name='users_finance_id',
        ),
        migrations.RenameField(
            model_name='item',
            old_name='shop',
            new_name='shop_id',
        ),
        migrations.RenameField(
            model_name='notification',
            old_name='users',
            new_name='user_id',
        ),
        migrations.RenameField(
            model_name='recommendations',
            old_name='users',
            new_name='user_id',
        ),
        migrations.RenameField(
            model_name='reportsettings',
            old_name='users',
            new_name='user_id',
        ),
        migrations.RenameField(
            model_name='shop',
            old_name='user',
            new_name='user_id',
        ),
        migrations.RenameField(
            model_name='supplier',
            old_name='user',
            new_name='user_id',
        ),
        migrations.RenameField(
            model_name='userdebtoritems',
            old_name='debtors',
            new_name='debtors_id',
        ),
        migrations.RenameField(
            model_name='userdebtoritems',
            old_name='items',
            new_name='items_id',
        ),
        migrations.RenameField(
            model_name='userdebtoritems',
            old_name='users',
            new_name='user_id',
        ),
        migrations.RenameField(
            model_name='userfinances',
            old_name='finances',
            new_name='finance_id',
        ),
        migrations.RenameField(
            model_name='userfinances',
            old_name='users',
            new_name='user_id',
        ),
        migrations.RenameField(
            model_name='usernotification',
            old_name='notifications',
            new_name='notification_id',
        ),
        migrations.RenameField(
            model_name='usernotification',
            old_name='users',
            new_name='user_id',
        ),
        migrations.AddField(
            model_name='debtor',
            name='user_id',
            field=models.ManyToManyField(blank=True, through='api.UserDebtorItems', to=settings.AUTH_USER_MODEL),
        ),
    ]