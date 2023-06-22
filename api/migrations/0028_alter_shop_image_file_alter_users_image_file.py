# Generated by Django 4.2.1 on 2023-06-22 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_alter_shopfinances_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='image_file',
            field=models.FileField(blank=True, null=True, upload_to='uploads/shop/images/'),
        ),
        migrations.AlterField(
            model_name='users',
            name='image_file',
            field=models.FileField(upload_to='uploads/user/images/'),
        ),
    ]
