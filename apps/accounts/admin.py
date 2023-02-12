from django.contrib import admin

from apps.accounts.models import User, UserContact, ChatGroup, GroupMember

admin.site.register(User)
admin.site.register(UserContact)
admin.site.register(ChatGroup)
admin.site.register(GroupMember)
