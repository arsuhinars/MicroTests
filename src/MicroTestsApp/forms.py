from django import forms
from PIL import Image
from .models import User


# Форма авторизации
class LoginForm(forms.Form):
    email = forms.EmailField(label='E-Mail', required=True)
    password = forms.CharField(label='Пароль', required=True,
        widget=forms.PasswordInput)

    # Проверка на ошибки
    def clean(self):
        form_data = self.cleaned_data
        if 'email' not in self.errors and 'password' not in self.errors:
            try:
                user = User.objects.get(email=form_data['email'])
                if not user.is_active:
                    self.add_error(None, 'Данный аккаунт был заблокирован администратором.')
                elif not user.is_confirmed:
                    self.add_error(None, 'Данный аккаунт ожидает подверждения.')
                elif not user.check_password(form_data['password']):
                    self.add_error(None, 'Вы указали неверный пароль.')
            except User.DoesNotExist:
                self.add_error(None, 'Аккаунт с таким E-Mail не существует.')
        return form_data


# Форма регистрации
class RegisterForm(forms.Form):
    firstName = forms.CharField(label='Имя', max_length=16, required=True)
    lastName = forms.CharField(label='Фамилия', max_length=16, required=True)
    email = forms.EmailField(label='E-Mail', required=True)
    password = forms.CharField(label='Пароль', required=True, max_length=16, min_length=8,
        widget=forms.PasswordInput)
    repeatPassword = forms.CharField(label='Повторите пароль', max_length=16, min_length=8, required=True,
        widget=forms.PasswordInput)

    # Собственная проверка на ошибки
    def clean(self):
        form_data = self.cleaned_data
        if 'password' not in self.errors and 'repeatPassword' not in self.errors:
            if form_data['password'] != form_data['repeatPassword']:
                self.add_error('repeatPassword', 'Пароли должны совпадать.')
        if 'email' not in self.errors:
            try:
                user = User.objects.get(email=form_data['email'])
                if not user.is_confirmed:
                    self.add_error(None, 'Данный аккаунт уже зарегестрирован и ожидает подверждения.')
                else:
                    self.add_error('email', 'Пользователь с таким E-Mail уже существует.')
            except User.DoesNotExist:
                pass
        return form_data


# Форма основных настроек
class GeneralSettingsForm(forms.Form):
    avatar = forms.ImageField(label='Фото', required=False)
    first_name = forms.CharField(label='Имя', max_length=16, required=True)
    last_name = forms.CharField(label='Фамилия', max_length=16, required=True)


# Форма смены пароля
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='Старый пароль', required=True, max_length=16, min_length=8,
        widget=forms.PasswordInput)
    new_password = forms.CharField(label='Новый пароль', required=True, max_length=16, min_length=8,
        widget=forms.PasswordInput)
    repeat_password = forms.CharField(label='Повторите пароль', required=True, max_length=16,
        min_length=8, widget=forms.PasswordInput)
    
    # Проверка на ошибки
    def clean(self):
        form_data = self.cleaned_data
        if 'new_password' not in self.errors and 'repeat_password' not in self.errors:
            if form_data['new_password'] != form_data['repeat_password']:
                self.add_error('repeat_password', 'Пароли должны совпадать.')
        return form_data

# Форма подверждения действия кодом
class ConfirmActionByCodeForm(forms.Form):
    code = forms.CharField(label='', required=True)

# Форма смены почты
class ChangeEmailForm(forms.Form):
    email = forms.EmailField(label='Адрес новой электронной почты', required=True)
