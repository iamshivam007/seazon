# Generated by Django 4.1.5 on 2023-02-16 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_chatgroup_premium'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_sync',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]