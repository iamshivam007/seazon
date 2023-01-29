from django.urls import path
from django.conf import settings

from apps.accounts import views as accounts_views
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", accounts_views.UserViewSet)

urlpatterns = [
    # API base url
    path("login/", accounts_views.LoginApiView.as_view()),
    path("verify-otp/", accounts_views.VerifyOtpApiView.as_view()),
    path("add-contacts/", accounts_views.AddNewContacts.as_view()),
] + router.urls
