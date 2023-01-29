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
