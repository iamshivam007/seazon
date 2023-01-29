# Generated by Django 4.1.5 on 2023-01-29 15:50

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_sync',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2023, 1, 29, 15, 50, 51, 384388, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='login_otp',
            field=models.CharField(blank=True, max_length=10, verbose_name='Login OTP'),
        ),
        migrations.AlterField(
            model_name='user',
            name='mobile_number',
            field=models.CharField(max_length=10, null=True, unique=True, verbose_name='Mobile Number'),
        ),
        migrations.CreateModel(
            name='UserContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name of User')),
                ('country_code', models.CharField(blank=True, max_length=4, verbose_name='User Country Code')),
                ('mobile_number', models.CharField(max_length=10, verbose_name='Mobile Number')),
                ('active', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]