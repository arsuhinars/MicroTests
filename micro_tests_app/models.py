from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class UserManager(BaseUserManager):
    """ Класс менеджера пользователей """

    def create_user(self, email, first_name, last_name, password=None):
        """ Метод регистрации пользователя """
        if not email:
            raise ValueError('E-Mail can\'t be None')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name)
        
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email, first_name, last_name, password)
        user.is_confirmed = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """ Класс пользователя """

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'first_name', 'last_name' ]

    def __str__(self):
        return self.email

    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}' 


    def send_mail(self, subject, message, from_email='noreply'):
        """
        Функция отправки электроного письма пользователю.
        *   Аргументы:
        *   subject - тема письма
        *   message - текст письма
        *   from_email - имя адреса отправителя (стандарт. 'noreply')
        """
        send_mail(subject, message, from_email, [self.email])


    def send_notification(self, title: str):
        """ Метод отправки уведомления пользователю """
        notification = Notification(user=self, title=title)
        notification.save()

    
    def get_notifications(self):
        """ Метод получения всех уведомления, адресованных текущему пользователю """
        notifications = Notification.objects.order_by('has_been_read').filter(user=self)
        return notifications

    
    def count_unread_notifications(self):
        """ Получить количество непрочитанных уведомлений """
        return len(Notification.objects.filter(user=self, has_been_read=False))


    def read_all_notifications(self):
        """ Метод прочтения всех уведомлений пользователя """
        Notification.objects.filter(user=self).update(has_been_read=True)


    @property
    def is_staff(self):
        return self.is_admin


class Notification(models.Model):
    """ Модель уведомления """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    url = models.CharField(max_length=64)
    send_time = models.DateTimeField(auto_now_add=True)
    has_been_read = models.BooleanField(default=False)


class TestModel(models.Model):
    """ Модель теста """

    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    publish_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)


class TaskModel(models.Model):
    """ Модель задачи """

    ONE_CHOISE = 0          # Задача с единственным ответом
    MULTIPLE_CHOISE = 1     # Задача с несколькими ответами

    # Виды задач
    TASK_TYPES = [
        (ONE_CHOISE, 'One choise'),
        (MULTIPLE_CHOISE, 'Multiple choise'),
    ]

    id = models.AutoField(primary_key=True)
    test = models.ForeignKey(TestModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.TextField()
    type = models.PositiveSmallIntegerField(choices=TASK_TYPES)
    options = models.TextField()
    answers = models.TextField()


class TestResult(models.Model):
    """ Модель результата прохождения теста """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(TestModel, on_delete=models.CASCADE)
    save_time = models.DateTimeField(auto_now_add=True)
    points = models.PositiveIntegerField()
    tasks_amount = models.PositiveIntegerField()
