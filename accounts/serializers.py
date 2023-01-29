import os
import random
import uuid

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from twilio.rest import Client


User = get_user_model()


account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "name", "country_code", "mobile_number"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name"]


class LoginSerializer(serializers.Serializer):
    country_code = serializers.CharField(max_length=5, validators=[RegexValidator("^(\+?\d{1,3}|\d{1,4})$")])
    mobile_number = serializers.CharField(max_length=10, validators=[RegexValidator("^\d{10}$")])

    class Meta:
        fields = ["country_code", "mobile_number"]

    def send_otp(self, validated_data):
        random_otp = random.randint(10000, 99999)
        client = Client(account_sid, auth_token)
        response = client.messages.create(
            from_=os.environ.get('TWILIO_PHONE_NUMBER'),
            to=validated_data["country_code"] + validated_data["mobile_number"],
            body=f'Hi, Your otp for verification is ${random_otp}'
        )
        print(response)
        user, _ = User.objects.get_or_create(defaults={"username": uuid.uuid4()}, **validated_data)
        user.login_otp = random_otp
        user.save()
        return


class VerifyOtpSerializer(serializers.Serializer):
    country_code = serializers.CharField(max_length=5, validators=[RegexValidator("^(\+?\d{1,3}|\d{1,4})$")])
    mobile_number = serializers.CharField(max_length=10, validators=[RegexValidator("^\d{10}$")])
    otp = serializers.CharField(max_length=10)

    class Meta:
        fields = ["country_code", "mobile_number", "otp"]

    def validate(self, attrs):
        user = User.objects.filter(
            country_code=attrs["country_code"],
            mobile_number=attrs["mobile_number"]
        ).first()
        if not user:
            raise ValidationError("Mobile number is not registered")
        if user.login_otp != attrs["otp"]:
            raise ValidationError("Invalid OTP")
        attrs["user"] = user
        return attrs

    def verify(self, validated_data):
        user = validated_data["user"]
        user.login_otp = ""
        user.save()
        return
