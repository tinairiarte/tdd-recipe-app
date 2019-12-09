from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUSerAdmin

from core import models


class UserAdmin(BaseUSerAdmin):
    ordering = ['id']
    list_display = ['email', 'name']


admin.site.register(models.User, UserAdmin)
