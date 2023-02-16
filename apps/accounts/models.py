import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for telegram.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    country_code = CharField(_("User Country Code"), blank=True, max_length=4)
    mobile_number = CharField(_("Mobile Number"), max_length=10, null=True, unique=True)
    login_otp = CharField(_("Login OTP"), blank=True, max_length=10)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    last_sync = models.DateTimeField()

    def __str__(self):
        return f"${self.name} -> ${self.mobile_number}"


class UserContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, null=True, blank=True)
    name = CharField(_("Name of User"), max_length=255)
    country_code = CharField(_("User Country Code"), blank=True, max_length=4)
    mobile_number = CharField(_("Mobile Number"), max_length=10)
    active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"${self.user} | ${self.name} -> ${self.mobile_number}"

    class Meta:
        unique_together = ['user', 'username']


class ChatGroup(models.Model):
    name = CharField(_("Name of the Group"), max_length=255)
    unique_id = models.UUIDField(default=uuid.uuid1, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    premium = models.BooleanField(default=False)

    def __str__(self):
        return f"${self.name} | ${self.created_by}"


class GroupMember(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"${self.group} | ${self.user}"

    class Meta:
        unique_together = ['group', 'user']
