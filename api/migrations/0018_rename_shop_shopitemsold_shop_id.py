# Generated by Django 4.2.1 on 2023-06-11 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_debtoritemsold_shopitemsold_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shopitemsold',
            old_name='shop',
            new_name='shop_id',
        ),
    ]
