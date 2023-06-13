# Generated by Django 4.2.1 on 2023-06-13 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_alter_shopitemsold_item_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='type',
            field=models.TextField(blank=True, choices=[('unit', 'Unidad'), ('gram', 'Gramos')], default='unit', null=True),
        ),
    ]
