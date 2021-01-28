from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import MicroTestsApp.utils as utils


""" Класс менеджера пользователей """
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

""" Класс пользователя """
class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=16, verbose_name=_('First name'))
    last_name = models.CharField(max_length=16, verbose_name=_('Last name'))
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True, verbose_name=_('Avatar'))
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_('Registration date'))
    last_login = models.DateTimeField(auto_now=True, verbose_name=_('Last login'))
    confirm_key = models.CharField(max_length=32, verbose_name=_('Confirm key'), null=True)
    is_confirmed = models.BooleanField(default=False, verbose_name=_('Is confirmed'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is active'))
    is_admin = models.BooleanField(default=False, verbose_name=_('Is admin'))

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

    @property
    def notifications(self):
        return Notification.objects.filter(receiving_user=self)

    @property
    def has_unread_notifies(self):
        return len(Notification.objects.filter(receiving_user=self, is_read=False)) > 0


""" Класс уведомления """
class Notification(models.Model):
    class Meta:
        verbose_name=_('Notification')
        verbose_name_plural=_('Notifications')

    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=64, verbose_name=_('Text'))
    url = models.URLField(verbose_name=_('URL'))
    is_read = models.BooleanField(default=False, verbose_name=_('Is read'))
    receiving_user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name=_('Receiving user'))
    send_date = models.DateTimeField(auto_now=True, verbose_name=_('Send date'))


""" Класс теста """
class TestModel(models.Model):
    class Meta:
        verbose_name=_('Test')
        verbose_name_plural=_('Tests')
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, verbose_name=_('Test name'))
    author = models.ForeignKey('User', models.CASCADE, verbose_name=_('Author'))
    create_date = models.DateTimeField(auto_now=True, verbose_name=_('Create date'))
    is_private = models.BooleanField(default=False, verbose_name=_('Is private'))


""" Модель одного задания в тесте """
class TaskModel(models.Model):
    class Meta:
        verbose_name=_('Task')
        verbose_name_plural=_('Tasks')
    
    id = models.AutoField(primary_key=True)
    test = models.ForeignKey('TestModel', models.CASCADE, verbose_name=_('Test'))
    name = models.CharField(max_length=32, verbose_name=_('Task name'))
    description = models.JSONField(verbose_name=_('Task description'))
