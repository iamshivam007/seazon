# Generated by Django 4.1.5 on 2023-02-23 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_chatgroup_unique_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatgroup',
            name='amount',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
