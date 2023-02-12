from django.utils import timezone
import os
import random
import uuid

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from twilio.rest import Client
from apps.accounts.models import UserContact, GroupMember, ChatGroup


User = get_user_model()


account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "name", "country_code", "mobile_number", "id"]


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
        client.messages.create(
            from_=os.environ.get('TWILIO_PHONE_NUMBER'),
            to=validated_data["country_code"] + validated_data["mobile_number"],
            body=f'Hi, Your otp for verification is ${random_otp}'
        )
        user, _ = User.objects.get_or_create(defaults={"username": uuid.uuid4(), "last_sync": timezone.now()}, **validated_data)
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


class UserContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserContact
        fields = ["name", "country_code", "mobile_number", "username"]


class UserContactsSerializer(serializers.Serializer):
    contacts = serializers.ListSerializer(child=UserContactSerializer())

    class Meta:
        fields = ["contacts"]

    def validate(self, attrs):
        # if len(attrs) >= 100:
        #     raise ValidationError("Please less less than 100 contacts")
        return attrs

    def save(self, **kwargs):
        mobile_numbers = map(lambda x: x["mobile_number"], self.validated_data["contacts"])
        existing_mobile_numbers = UserContact.objects.filter(
            user=self.context["request"].user,
            mobile_number__in=mobile_numbers
        ).values_list("mobile_number", flat=True)

        # Filter out existing number
        new_data = list(filter(lambda x: x["mobile_number"] not in existing_mobile_numbers, self.validated_data["contacts"]))
        mobile_number_username_map = dict(User.objects.filter(
            mobile_number__in=map(lambda x: x["mobile_number"], new_data)
        ).values_list("mobile_number", "username"))

        new_contacts = list(map(lambda item: UserContact(
            user=self.context["request"].user,
            mobile_number=item["mobile_number"],
            country_code=item["country_code"],
            name=item["name"],
            username=mobile_number_username_map.get(item["mobile_number"]),
            active=bool(mobile_number_username_map.get(item["mobile_number"])),
            updated_at=timezone.now()
        ), new_data))
        UserContact.objects.bulk_create(new_contacts)
        return list(filter(lambda item: item.username is not None, new_contacts))


class ChatGroupSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    )
    creator_mobile_number = serializers.CharField(source="created_by.mobile_number", read_only=True)

    class Meta:
        model = ChatGroup
        fields = '__all__'

    def create(self, validated_data):
        users = validated_data.pop("users")
        instance = super().create(validated_data)
        group_members = [GroupMember(user=self.context["request"].user, group=instance, is_admin=True)]
        for user in users:
            group_members.append(GroupMember(
                user=user, group=instance
            ))
        GroupMember.objects.bulk_create(group_members)
        return instance


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = '__all__'
