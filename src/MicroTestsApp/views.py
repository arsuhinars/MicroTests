import os
import django.contrib.auth as auth
from io import BytesIO
from random import randint
from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from django.conf import settings as project_settings
from MicroTestsApp import forms
from MicroTestsApp.models import User
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
                    form.add_error('code', 'Указан неверный код')
            return HttpResponse(form.errors.as_json())

        form = forms.ChangePasswordForm(request.POST)
        if form.is_valid():
            # Проверяем старый пароль
            if user.check_password(form.cleaned_data['old_password']):
                # Если прошлый пароль равен новому
                if form.cleaned_data['old_password'] == form.cleaned_data['new_password']:
                    form.add_error('new_password', 'Пароли должны отличаться')
                else:
                    # Сохраняем код для подверждения в кэше
                    if not cache.get(code_key):
                        cache.set(code_key, str(randint(10000, 99999)), 60)
                        cache.set(pass_key, form.cleaned_data['new_password'], 60)
                    # Отправляем код пользователю
                    user.send_mail('MicroTests - смена пароля',
                        f'''На сайте была запрошена смена пароля. Код для смены пароля указан ниже.
Если вы этого не делали, то проигнорируйте это письмо.
Код подверждения: {cache.get(code_key)}

Не пытайтесь отвечать на это письмо. Оно было отправлено автоматически.''')
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
                    form.add_error('code', 'Указан неверный код')
            return HttpResponse(form.errors.as_json())

        form = forms.ChangeEmailForm(request.POST)
        if form.is_valid():
            # Если прошлая почта равен новой
            if form.cleaned_data['email'] == user.email:
                form.add_error('email', 'Почта должна отличаться от текущей')
            else:
                # Сохраняем код для подверждения в кэше
                if not cache.get(code_key):
                    cache.set(code_key, str(randint(10000, 99999)), 60)
                    cache.set(email_key, form.cleaned_data['email'], 60)
                # Отправляем код пользователю
                send_mail('MicroTests - смена почты',
                    f'''На сайте был сделан запрос на изменение электронной почты на данный.
Код для смены почты указан ниже. Если вы этого не делали, то проигнорируйте это письмо.
Код подверждения: {cache.get(code_key)}

Не пытайтесь отвечать на это письмо. Оно было отправлено автоматически.''',
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
            send_mail(
                'MicroTests - подверждение аккаунта',
                f'''На ваш адрес электронной почты был зарегестрирован аккаунт на сайте MicroTests. 
Если вы не регистрировались на нашем сайте, то проигнорируйте это сообщение.
Для активации аккаунта перейдите по ссылке:
{request.build_absolute_uri(f'/confirm/?key={user.confirm_key}')}.

Не пытайтесь отвечать на это письмо. Оно было отправлено автоматически.''',
                'noreply', [user.email])
            if not request.is_ajax():
                return HttpResponseRedirect('/confirm')
        # Отправляем json массив с ошибками, если это ajax запрос
        if request.is_ajax():
            return HttpResponse(form.errors.as_json())
    return render(request, 'register.html', {'form': form})


def confirm(request):
    """ Страница подвержения аккаунта """
    context = {
        'subject': 'Регистрация',
        'title': 'Спасибо за регистрацию.',
        'message': '''Чтобы закончить регистрацию вы должны перейти по ссылке,
        указанной в высланном письме на ваш электронный адрес.''',
        'buttons': []
    }
    if 'key' in request.GET:
        try:
            # Ищем пользователя с данным ключом
            user = User.objects.get(confirm_key=request.GET['key'], is_confirmed=False)
            user.confirm_key = None
            user.is_confirmed = True
            user.save()
            context['message'] = 'Ваш аккаунт был успешно подвержден. Теперь вы можете войти в него.'
            context['buttons'].append({
                'text': 'Войти',
                'url': '/login/'
            })
        except User.DoesNotExist:
            return HttpResponseRedirect('/')
    context['buttons'].append({
        'text': 'Вернуться на главную',
        'url': '/'
    })
    return render(request, 'message.html', context)
