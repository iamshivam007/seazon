# Generated by Django 4.1.5 on 2023-02-16 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_groupmember_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatgroup',
            name='premium',
            field=models.BooleanField(default=False),
        ),
    ]
