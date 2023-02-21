import datetime

from django.utils import timezone

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from apps.accounts.serializers import UserSerializer, LoginSerializer, VerifyOtpSerializer, ProfileUpdateSerializer, UserContactsSerializer, UserContactSerializer
from apps.accounts.models import UserContact, ChatGroup, GroupMember
from apps.accounts import serializers as accounts_serializers

User = get_user_model()


class UserViewSet(RetrieveModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "mobile_number"

    permission_classes = (IsAuthenticated, )

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset

    @action(detail=False, methods=["GET"])
    def sync(self, request):
        serializer = UserSerializer(
            list(UserContact.objects.filter(
                user=self.request.user, updated_at__gte=self.request.user.last_sync,
                username__isnull=False
            ).exclude(username__exact='')),
            context={"request": request},
            many=True
        )
        self.request.user.last_sync = timezone.now()
        self.request.user.save()
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["GET", "PUT"])
    def me(self, request):
        if request.method == "GET":
            serializer = UserSerializer(request.user, context={"request": request})
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            serializer = ProfileUpdateSerializer(data=request.data, instance=self.request.user)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_200_OK)


class ChatGroupViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = accounts_serializers.ChatGroupSerializer
    queryset = ChatGroup.objects.all()
    lookup_field = "unique_id"

    permission_classes = (IsAuthenticated, )

    def get_queryset(self, *args, **kwargs):
        queryset = self.queryset
        if self.request.query_params.get("premium") in [True, "true"]:
            queryset = queryset.filter(premium=True)
        elif self.request.query_params.get("premium") in [False, "false"]:
            queryset = queryset.filter(premium=False)
        return queryset.prefetch_related('groupmember_set__user')

    @action(detail=False, methods=["GET"])
    def mine(self, *args, **kwargs):
        queryset = self.queryset.filter(
            groupmember__user=self.request.user).distinct().prefetch_related('groupmember_set__user'
        )
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def add_member(self, request, *args, **kwargs):
        data = dict(**request.data, group=self.get_object().id, user=User.objects.get(username=request.data.get("username")).id)
        serializer = accounts_serializers.GroupMemberSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def join(self, request, *args, **kwargs):
        data = dict(**request.data, group=self.get_object().id, user=request.user.id)
        serializer = accounts_serializers.GroupMemberSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def exit(self, request, *args, **kwargs):
        GroupMember.objects.filter(group=self.get_object(), user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginApiView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_otp(serializer.validated_data)
        return Response(status=status.HTTP_200_OK)


class VerifyOtpApiView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.verify(serializer.validated_data)
        user = serializer.validated_data["user"]

        UserContact.objects.filter(
            mobile_number=user.mobile_number
        ).update(
            username=user.username,
            updated_at=timezone.now(),
            active=True
        )
        user.last_sync = timezone.datetime(2022, 1, 1)
        user.save()

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "name": user.name,
            "username": user.username,
            "id": user.id
        }, status=status.HTTP_200_OK)


class AddNewContacts(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = UserContactsSerializer(data=request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        new_contacts = serializer.save()
        return Response(data=UserContactSerializer(new_contacts, many=True).data, status=status.HTTP_200_OK)
