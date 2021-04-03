from django import forms

from .models import *

TEXT_INPUT_WIDGET = forms.TextInput(attrs={'class': 'form-control mb-3 d-block'})
TEXT_AREA_WIDGET = forms.Textarea(attrs={'class': 'form-control mb-3 d-block'})
PASSWORD_INPUT_WIDGET = forms.PasswordInput(attrs={'class': 'form-control mb-3 d-block'})

class LoginForm(forms.Form):
    """ Форма авторизации пользователя """

    email = forms.EmailField(label='E-Mail', widget=TEXT_INPUT_WIDGET)
    password = forms.CharField(label='Пароль', widget=PASSWORD_INPUT_WIDGET)

    def clean(self):
        """ Метод проверки на наличие ошибок """
        form_data = self.cleaned_data
        if 'email' not in self.errors and 'password' not in self.errors:
            try:
                user = User.objects.get(email=form_data['email'])
                if not user.is_active:
                    self.add_error('email', 'Данный аккаунт был заблокирован.')
                elif not user.check_password(form_data['password']):
                    self.add_error('password', 'Вы указали неверный пароль.')
            except User.DoesNotExist:
                self.add_error('email', 'Аккаунт с таким E-Mail не существует.')
        return form_data


class RegisterForm(forms.Form):
    """ Форма регистрации пользователя """

    email = forms.EmailField(label='E-Mail', widget=TEXT_INPUT_WIDGET)
    first_name = forms.CharField(label='Имя', widget=TEXT_INPUT_WIDGET)
    last_name = forms.CharField(label='Фамилия', widget=TEXT_INPUT_WIDGET)
    password = forms.CharField(label='Пароль',
        widget=PASSWORD_INPUT_WIDGET, min_length=8)
    repeat_password = forms.CharField(label='Повторите пароль',
        widget=PASSWORD_INPUT_WIDGET, min_length=8)
    
    def clean(self):
        """ Метод проверки на наличие ошибок """
        form_data = self.cleaned_data
        if 'password' not in self.errors and 'repeat_password' not in self.errors:
            if self.cleaned_data['password'] != self.cleaned_data['repeat_password']:
                self.add_error('repeat_password', 'Пароли должны совпадать.')
        if 'email' not in self.errors:
            try:
                User.objects.get(email=form_data['email'])
                self.add_error('email', 'Пользователь с таким адресом уже существует.')
            except User.DoesNotExist:
                pass
        return form_data


class ProfileSettingsForm(forms.Form):
    """ Форма настроек профиля """

    email = forms.EmailField(label='Новый E-Mail', widget=TEXT_INPUT_WIDGET)
    first_name = forms.CharField(label='Имя', widget=TEXT_INPUT_WIDGET)
    last_name = forms.CharField(label='Фамилия', widget=TEXT_INPUT_WIDGET)
    password = forms.CharField(label='Новый пароль',
        widget=PASSWORD_INPUT_WIDGET, min_length=8, required=False)
    repeat_password = forms.CharField(label='Повторите новый пароль',
        widget=PASSWORD_INPUT_WIDGET, min_length=8, required=False)
    
    def clean(self):
        """ Метод проверки на ошибки """
        form_data = self.cleaned_data
        if 'password' not in self.errors and \
           'repeat_password' not in self.errors and \
           (form_data['password'] or form_data['repeat_password']):
            if self.cleaned_data['password'] != self.cleaned_data['repeat_password']:
                self.add_error('repeat_password', 'Пароли должны совпадать.')
        return form_data


class EditTestForm(forms.Form):
    """ Форма редактирования теста """

    name = forms.CharField(label='Название', widget=TEXT_INPUT_WIDGET)
    category = forms.CharField(label='Категория', widget=TEXT_INPUT_WIDGET)
    description = forms.CharField(
        label='Описание (допускается использование HTML тегов)',
        widget=TEXT_AREA_WIDGET, required=False)
