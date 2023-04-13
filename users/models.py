from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from .managers import CustomUserManager
from dotenv import load_dotenv
import os
import cryptocode
load_dotenv()

# Create your models here.
#NOTE this class is DEPRECATED and doesn't work properly, just kept to not cause issues during migration
class CustomPasswordField(models.CharField):
    description = "Custom Encrypted Password Field"
    
    def __init__(self, *args, **kwargs):
        self.__password_key = os.getenv('PASSWORD_KEY_STRING')
        super().__init__(*args, **kwargs)
    
    def get_prep_value(self, value: str) -> str:
        return cryptocode.encrypt(self.__password_key, value)
    
    def from_db_value(self, value : str, expression, connection) -> str:
        if value is None:
            return value
        dec = cryptocode.decrypt(self.__password_key, value)
        if type(dec) == str:
            return dec
    
    def to_python(self, value: str) -> str:
        if value is None:
            return value
        dec = cryptocode.decrypt(self.__password_key, value)
        if type(dec) == str:
            return dec

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=20)
    last_name = models.CharField(_('last name'), max_length=20)
    phone_number = models.CharField(_('phone number'), max_length=14)

    demo_login = models.CharField(_('demo login'), blank=False, null=False, max_length=12)
    demo_password = models.CharField(_('demo password'), blank=False, null=False, max_length=255)
    demo_server = models.CharField(_('demo server'), blank=False, null=False, max_length=20)

    live_login = models.CharField(_('live login'), blank=False, null=False, max_length=12)
    live_password = models.CharField(_('live password'), blank=False, null=False, max_length=255)
    live_server = models.CharField(_('live server'), blank=False, null=False, max_length=20)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 
                       'demo_login', 'demo_password', 'demo_server',
                       'live_login', 'live_password', 'live_server'
                       ]

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.demo_password = cryptocode.encrypt(os.getenv('PASSWORD_KEY_STRING'), self.demo_password)
            self.live_password = cryptocode.encrypt(os.getenv('PASSWORD_KEY_STRING'), self.live_password)
        super().save(*args, **kwargs)

    def get_demo_password(self):
        return cryptocode.decrypt(os.getenv('PASSWORD_KEY_STRING'), self.demo_password)

    def get_live_password(self):
        return cryptocode.decrypt(os.getenv('PASSWORD_KEY_STRING'), self.live_password)
