from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import MicroTestsApp.utils as utils


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('E-Mail can\'t be None')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name)
        
        user.confirm_key = utils.generate_random_string()
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_confirmed = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=16, verbose_name='Имя')
    last_name = models.CharField(max_length=16, verbose_name='Фамилия')
    avatar = models.ImageField(upload_to='avatars', null=True, verbose_name='Аватар')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    last_login = models.DateTimeField(auto_now=True, verbose_name='Последний вход')
    confirm_key = models.CharField(max_length=32, verbose_name='Ключ для подвержения аккаунта', null=True)
    is_confirmed = models.BooleanField(default=False, verbose_name='Подвержден-ли')
    is_active = models.BooleanField(default=True, verbose_name='Активен-ли')
    is_admin = models.BooleanField(default=False, verbose_name='Является ли администратором')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'first_name', 'last_name' ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.last_name} {self.first_name}'

    def get_short_name(self):
        return self.first_name

    def send_mail(self, subject, message, from_email='noreply'):
        """
        Функция отправки электроного письма пользователю.
        *   Аргументы:
        *   subject - тема письма
        *   message - текст письма
        *   from_email - имя адреса отправителя (стандарт. 'noreply')
        """
        send_mail(subject, message, from_email, [self.email])

    @property
    def is_staff(self):
        return self.is_admin
