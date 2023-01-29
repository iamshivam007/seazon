from django.contrib import admin

from accounts.models import User, UserContact

admin.site.register(User)
admin.site.register(UserContact)
