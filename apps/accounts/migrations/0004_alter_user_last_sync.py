# Generated by Django 4.1.5 on 2023-02-05 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_usercontact_username_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_sync',
            field=models.DateTimeField(),
        ),
    ]
