from django.db import models
import pyotp
import datetime
from django.utils import timezone
from urllib.parse import urlparse
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class MyUserManager(BaseUserManager):
    def create_user(self, phone_no, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not phone_no:
            raise ValueError('Users must have an phone no')

        user = self.model(
            phone_no=phone_no
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_no, password):
        """
        Creates and saves a superuser with the given phoneno and password.
        """
        user = self.create_user(
            phone_no=phone_no,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
# Create your models here.

class User(AbstractBaseUser):
    phone_no = models.CharField(max_length = 10 , unique=True)
    password = models.CharField(max_length= 6)
    is_active = models.BooleanField(('active'), default=True)
    is_verified = models.BooleanField(('verified'),default=False)
    is_admin = models.BooleanField(default=False)
    
    objects = MyUserManager()
    USERNAME_FIELD = 'phone_no'

    def __str__(self):
        return self.phone_no
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
class Link(models.Model):
    linkid = models.AutoField(primary_key = True)
    created_date = models.DateTimeField(blank=True, default=timezone.now)
    shortenURL= models.CharField(max_length=500,unique=True)
    targetURL= models.CharField(max_length=500)
    last_hit = models.DateTimeField(blank=True, default=timezone.now)
    hit_count = models.PositiveIntegerField(default = 0)

    def clean(self):
        targetURL=self.targetURL.lower()
        if urlparse(targetURL).scheme=='':
            targetURL='http://'+targetURL
        return targetURL
