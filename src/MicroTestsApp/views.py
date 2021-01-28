import os
import django.contrib.auth as auth
from io import BytesIO
from random import randint
from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from django.conf import settings as project_settings
from MicroTestsApp import forms
from MicroTestsApp.models import User, Notification
import MicroTestsApp.utils as utils


def index(request):
    """ Главная страница """
    return render(request, 'index.html')


def profile(request, email):
    """ Страница пользователя """
    try:
        user = User.objects.get(email=email)
        return render(request, 'profile.html', {'profile':user})
    except User.DoesNotExist:
        return HttpResponseNotFound()


def settings(request):
    """ Страница настроек пользователя """
    # Если пользователь не вошел в аккаунт
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    
    change_password_form = forms.ChangePasswordForm()
    change_email_form = forms.ChangeEmailForm()
    confirm_action_form = forms.ConfirmActionByCodeForm()
    if request.method == 'GET':
        general_form = forms.GeneralSettingsForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })
    elif request.method == 'POST':
        general_form = forms.GeneralSettingsForm(request.POST, request.FILES)
        # Проверяем на ошибки
        if general_form.is_valid():
            user = request.user
            avatar = general_form.cleaned_data.get('avatar', None)      # Получаем отправленное изображение
            if avatar:
                image_name = utils.generate_random_string(16) + '.jpg'  # Генерируем имя файла
                image = utils.crop_image_rect(Image.open(avatar), 64)   # Вмещаем в квадрат и уменьшаем разрешение до 64x64
                buffer = BytesIO()
                image.save(buffer, format='JPEG')
                content = ContentFile(buffer.getvalue())

                if user.avatar:
                    path = os.path.join(project_settings.MEDIA_ROOT, user.avatar.name)
                    if os.path.exists(path):
                        os.remove(path)     # Удаляем старое изображение
                user.avatar.save(image_name, content)   # Сохраняем
            user.first_name = general_form.cleaned_data['first_name']
            user.last_name = general_form.cleaned_data['last_name']
            user.save()
        # Отправляем json массив с ошибками, если это ajax запрос
        if request.is_ajax():
            return HttpResponse(general_form.errors.as_json())
    return render(request, 'settings.html', {
        'general_form':general_form,
        'change_password_form': change_password_form,
        'change_email_form': change_email_form,
        'confirm_action_form': confirm_action_form})


def change_password(request):
    """ Страница для изменения пароля """
    if request.method == 'POST':
        user = request.user
        # Если пользователь не авторизован
        if not user.is_authenticated:
            return HttpResponseRedirect('/login')
        # Имена ключей в кэше
        code_key = user.email + '_password_confirm_code'
        pass_key = user.email + '_new_password'

        # Если был отправлен код для смены пароля
        if 'code' in request.POST:
            form = forms.ConfirmActionByCodeForm(request.POST)
            if form.is_valid():
                # Если код был указан правильный
                if form.cleaned_data['code'] == cache.get(code_key):
                    user.set_password(cache.get(pass_key))
                    user.save()
                    # Авторизируем пользователя повторно
                    auth.login(request, user)

                    # Удаляем коды подверждения из кэша
                    cache.delete_many([code_key, pass_key])
                else:
                    # Translators: Сообщение о указании неверного кода из сообщения
                    form.add_error('code', _('Wrong code was written'))
            return HttpResponse(form.errors.as_json())

        form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            # Проверяем старый пароль
            if user.check_password(form.cleaned_data['old_password']):
                # Если прошлый пароль равен новому
                if form.cleaned_data['old_password'] == form.cleaned_data['new_password']:
                    form.add_error('new_password', _('Passwords should be different'))
                else:
                    # Сохраняем код для подверждения в кэше
                    if not cache.get(code_key):
                        cache.set(code_key, str(randint(10000, 99999)), 60)
                        cache.set(pass_key, form.cleaned_data['new_password'], 60)
                    # Отправляем код пользователю
                    # Translators: сообщение с кодом для подверждения смены пароля
                    user.send_mail(
                        _('Password changing message subject', 'Email message'),
                        _('Password changing message text', 'Email message').format(cache.get(code_key)))
            else:   # Если был указан неверный пароль
                form.add_error('old_password', 'Указан неверный пароль')
        return HttpResponse(form.errors.as_json())
    return HttpResponseNotFound()


def change_email(request):
    """ Страница для изменения почты """
    if request.method == 'POST':
        user = request.user
        # Если пользователь не авторизован
        if not user.is_authenticated:
            return HttpResponseRedirect('/login')

        # Имена ключей в кэше
        code_key = user.email + '_email_confirm_code'
        email_key = user.email + '_new_email'

        # Если был отправлен код для смены пароля
        if 'code' in request.POST:
            form = forms.ConfirmActionByCodeForm(request.POST)
            if form.is_valid():
                # Если код был указан правильный
                if form.cleaned_data['code'] == cache.get(code_key):
                    user.email = cache.get(email_key)
                    user.save()
                    # Авторизируем пользователя повторно
                    auth.login(request, user)

                    # Удаляем коды подверждения из кэша
                    cache.delete_many([code_key, email_key])
                else:
                    form.add_error('code', _('Wrong code was written'))
            return HttpResponse(form.errors.as_json())

        form = forms.ChangeEmailForm(request.POST)
        if form.is_valid():
            # Если прошлая почта равен новой
            if form.cleaned_data['email'] == user.email:
                form.add_error('email', _('Email should differ from old'))
            else:
                # Сохраняем код для подверждения в кэше
                if not cache.get(code_key):
                    cache.set(code_key, str(randint(10000, 99999)), 60)
                    cache.set(email_key, form.cleaned_data['email'], 60)
                # Отправляем код пользователю
                # Translators: сообщение с кодом для подверждения смены почты
                send_mail(
                    _('Email changing message subject', 'Email message'), 
                    _('Email changing message text', 'Email message').format(cache.get(code_key)),
                    'noreply', [form.cleaned_data['email']])
        return HttpResponse(form.errors.as_json())
    return HttpResponseNotFound()


def login(request):
    """ Страница входа """
    # Если пользователь уже вошел в аккаунт
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.method == 'GET':
        form = forms.LoginForm()
    elif request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            # Авторизируем пользователя
            auth.login(request, User.objects.get(email=form.cleaned_data['email']))
            if not request.is_ajax():
                return HttpResponseRedirect('/')
        # Отправляем json массив с ошибками, если это ajax запрос
        if request.is_ajax():
            return HttpResponse(form.errors.as_json())
    return render(request, 'login.html', {'form': form})


def logout(request):
    """ Страница выхода из аккаунта """
    auth.logout(request)
    return HttpResponseRedirect('/')


def register(request):
    """ Страница регистрации """
    # Если пользователь уже вошел в аккаунт
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.method == 'GET':
        form = forms.RegisterForm()
    elif request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            # Регистрируем пользователя
            user = User.objects.create_user(
                form.cleaned_data['email'],
                form.cleaned_data['firstName'],
                form.cleaned_data['lastName'],
                form.cleaned_data['password'])
            # Шлем сообщение с ссылкой для активации аккаунта
            # Translators: сообщения с ссылкой для подверждения регистрации
            user.send_mail(
                _('Registration confirm message subject'),
                _('Registration confirm message text').format(
                    request.build_absolute_uri(f'/confirm/?key={user.confirm_key}')))
            if not request.is_ajax():
                return HttpResponseRedirect('/confirm')
        # Отправляем json массив с ошибками, если это ajax запрос
        if request.is_ajax():
            return HttpResponse(form.errors.as_json())
    return render(request, 'register.html', {'form': form})


def confirm(request):
    """ Страница подвержения аккаунта """
    context = {
        'subject': _('Registration'),
        'title': _('Thank you for registration.'),
        # Translators: сообщение говорящее, что необходимо подвердить аккаунт через отправленное письмо
        'message': _('Registration confirm page text'),
        'buttons': []
    }
    if 'key' in request.GET:
        try:
            # Ищем пользователя с данным ключом
            user = User.objects.get(confirm_key=request.GET['key'], is_confirmed=False)
            user.confirm_key = None
            user.is_confirmed = True
            user.save()
            # Translators: сообщение, появляющееся после подверждения аккаунта 
            context['message'] = _('Your account was successful confirm.')
            context['buttons'].append({
                'text': _('Login'),
                'url': '/login/'
            })
        except User.DoesNotExist:
            return HttpResponseRedirect('/')
    context['buttons'].append({
        'text': _('Back to main'),
        'url': '/'
    })
    return render(request, 'message.html', context)


def read_notify(request):
    """ Страница, на которую необходимо отправлять пользователя,
        для того чтобы отметить уведомление прочитанным и переадресовать
        на его содержание."""
    if request.method == 'POST' or not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    notify_id = request.GET.get('notify_id')
    if notify_id:
        notify = Notification.objects.get(id=notify_id, receiving_user=request.user)
        notify.is_read = True
        notify.save()
        return HttpResponseRedirect(notify.url)
    return HttpResponseRedirect('/')


""" Класс отрисовщик форматированого текста """
# class FormatView():