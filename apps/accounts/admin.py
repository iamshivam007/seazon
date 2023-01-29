from django.contrib import admin

from apps.accounts.models import User, UserContact

admin.site.register(User)
admin.site.register(UserContact)
