from django.contrib import admin
from basicapp import models
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(models.Link)
admin.site.register(models.User)
admin.site.unregister(Group)
