import json

from django.http.response import *
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from .forms import *

def handler404(request, exception):
    """ Обработчик ошибки 404 - не найдено """
    return render(request, 'error.html', {
        'title': 'Страница не найдена!',
        'message': 'Страница, которую вы пытаетесь найти, не существует.'
    })


def handler500(request):
    """ Обработчик ошибки 500 - внутренняя ошибка сервера """
    return render(request, 'error.html', {
        'title': 'Произошла ошибка!',
        'message': 'Произошла внутренняя ошибка сервера. Попробуйте перезагрузить страницу или зайти на неё позже.'
    })


def handler403(request, exception):
    """ Обработчик ошибки 403 - доступ запрещен """
    return render(request, 'error.html', {
        'title': 'Доступ запрещен!',
        'message': 'У вас недостаточно прав для того, чтобы посетить данную страницу.'
    })


def handler400(request, exception):
    """ Обработчик ошибки 400 - неправильный формат запроса """
    return render(request, 'error.html', {
        'title': 'Неправильный запрос!',
        'message': 'Обнаружена ошибка в формате запроса данной страницы. Попробуйте перезагрузить её или зайти позже.'
    })


def authorization(request):
    """ Страница авторизации """

    # Если пользователь уже авторизован
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    return render(request, 'authorization.html')


def login(request):
    """ Страница входа """

    # Если пользователь уже авторизован
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        login_form = LoginForm(request.POST)

        # Если форма заполнена правильно
        if login_form.is_valid():
            # Авторизуем пользователя
            auth.login(request, User.objects.get(email=login_form.cleaned_data['email']))
            return HttpResponsePermanentRedirect('/')
    else:
        login_form = LoginForm()

    return render(request, 'login.html', {'login_form': login_form})


def register(request):
    """ Страница регистрации """

    # Если пользователь уже авторизован
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)

        # Если форма заполнена правильно
        if register_form.is_valid():
            # Регистрируем пользователя
            auth.login(request, User.objects.create_user(
                register_form.cleaned_data['email'],
                register_form.cleaned_data['first_name'],
                register_form.cleaned_data['last_name'],
                register_form.cleaned_data['password']))
            return HttpResponsePermanentRedirect('/')
    else:
        register_form = RegisterForm()

    return render(request, 'register.html', {'register_form': register_form})


@login_required
def notifications(request):
    """ Страница списка уведомлений """
    return render(request, 'notifications.html')


@login_required
def settings(request):
    """ Страница настроек профиля """

    if request.method == 'POST':
        settings_form = ProfileSettingsForm(request.POST)
        # Если форма заполнена правильно
        if settings_form.is_valid():
            form_data = settings_form.cleaned_data

            # Если адрес почты был изменен
            if request.user.email != form_data['email']:
                try:
                    # Если существует пользователь с таким же адресом
                    User.objects.get(email=form_data['email'])
                    settings_form.add_error('email', 'Пользователь с таким адресом уже существует.')
                except User.DoesNotExist:
                    pass
            
            # Продолжаем только если нет остальных ошибок
            if settings_form.is_valid():
                request.user.email = form_data['email']
                request.user.first_name = form_data['first_name']
                request.user.last_name = form_data['last_name']
                # Если указан новый пароль
                if form_data['password']:
                    request.user.set_password(form_data['password'])
            
                request.user.save()

                # По новой авторизуем пользователя
                auth.login(request, request.user)
    else:
        settings_form = ProfileSettingsForm(initial={
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })

    return render(request, 'settings.html', {'settings_form': settings_form})


@login_required
def logout_view(request):
    """ Страница для выхода из аккаунта """
    auth.logout(request)
    return HttpResponsePermanentRedirect('/')


@login_required
def notification(request, id):
    """ Страница для чтения уведомления """

    notification = Notification.objects.get(id=id)
    if notification.user != request.user:
        return HttpResponseNotAllowed()

    notification.has_been_read = True
    notification.save()

    return HttpResponseRedirect(notification.url)


@login_required
def index(request):
    """ Главная страница """

    return render(request, 'index.html')


@login_required
def tests_list(request):
    """ Страница со списком тестов """

    categories = {}
    tests = TestModel.objects.all()
    for test in tests:
        if test.category not in categories:
            categories[test.category] = []
        categories[test.category].append({
            'name': test.name,
            'url': f'/test/{test.id}'   
        })

    return render(request, 'tests_list.html', {'categories': categories})


@login_required
def test_view(request, test_id):
    """ Страница для прохождения теста """

    try:
        test = TestModel.objects.get(id=test_id)
    except TestModel.DoesNotExist:
        return HttpResponseNotFound()

    tasks = TaskModel.objects.filter(test=test)
    
    try:
        best_result = TestResult.objects.filter(user=request.user, test=test).order_by('-points')[0]
    except IndexError:
        best_result = None

    return render(request, 'test.html', { 'test':test, 'tasks_amount': len(tasks), 'best_result': best_result })


@login_required
def task_view(request, test_id, task_index):
    """ Страница для задания в тесте """

    try:
        test = TestModel.objects.get(id=test_id)
    except TestModel.DoesNotExist:
        return HttpResponseNotFound()

    tasks = TaskModel.objects.filter(test=test)

    if task_index < 0 or task_index >= len(tasks):
        return HttpResponseNotFound()

    task = tasks[task_index]

    # Загружаем ответы в формате JSON
    options = json.loads(task.options)

    # Очищаем список, чтобы его заполнить новыми объектами
    task.options = []

    # Формируем объекты ответов подходящего формата
    for i in range(len(options)):
        task.options.append({
            'index': i,
            'text': options[i]
        })

    return render(request, 'task.html', {'task': task, 'task_index': task_index, 'task_amount': len(tasks)})


@login_required
def save_result(request):
    """ Страница для сохранения результата прохождения теста """

    if request.method != 'POST' or \
       'test_id' not in request.POST or \
       'answers' not in request.POST:
        return HttpResponseBadRequest()

    try:
        test_id = int(request.POST['test_id'])
    except ValueError:
        return HttpResponseBadRequest()

    try:
        answers = json.loads(request.POST['answers'])
        if not isinstance(answers, list):
            return HttpResponseBadRequest()
    except json.decoder.JSONDecodeError:
        return HttpResponseBadRequest()

    try:
        test = TestModel.objects.get(id=test_id)
    except TestModel.DoesNotExist:
        return HttpResponseBadRequest()

    points = 0

    tasks = TaskModel.objects.filter(test=test)

    if len(tasks) != len(answers):
        return HttpResponseBadRequest()
    
    for i in range(len(tasks)):
        if tasks[i].type == TaskModel.ONE_CHOISE:
            if tasks[i].answers == str(answers[i]):
                points += 1
        elif len(set(json.loads(tasks[i].answers)) - set(answers[i])) == 0:
            points += 1
    
    result = TestResult(user=request.user, test=test, points=points, tasks_amount=len(tasks))
    result.save()
    
    return HttpResponse('ok')


@login_required
def results(request, test_id):
    """ Страница для просмотра своих результатов """

    try:
        test = TestModel.objects.get(id=test_id)
    except TestModel.DoesNotExist:
        return HttpResponseNotFound()

    results = TestResult.objects.filter(user=request.user, test=test).order_by('-save_time')

    results_amount = len(results)

    if not request.GET.get('show_all'):
        results = results[:5]

    return render(request, 'results.html', {
        'just': request.GET.get('just'),
        'show_all': request.GET.get('show_all'),
        'test': test,
        'results': results,
        'results_amount': results_amount
    })


@login_required
def all_results(request, test_id, page):
    """ Страница для просмотра результатов всех пользователей """

    if not request.user.is_admin:
        return HttpResponseForbidden()

    try:
        test = TestModel.objects.get(id=test_id)
    except TestModel.DoesNotExist:
        return HttpResponseNotFound()

    users = User.objects.all()

    max_pages = len(users) // 10 + (1 if len(users) % 10 else 0)

    if page < 0 or page >= max_pages:
        return HttpResponseNotFound()

    users = users[page * 10:(page + 1) * 10]

    results = []
    for user in users:
        user_results = TestResult.objects.filter(user=user, test=test).order_by('-points')
        if len(user_results) > 0:
            results.append({
                'user_id': user.id,
                'user_email': user.email,
                'user_name': user.full_name,
                'result': f'{user_results[0].points}/{user_results[0].tasks_amount}'
            })

    return render(request, 'all_results.html', {
        'test': test,
        'results': results,
        'page': page,
        'max_pages': max_pages,
        'pages_before': range(max(page - 3, 0), page),
        'pages_after': range(page + 1, min(page + 4, max_pages)),
    })


@login_required
def create_test(request):
    """ Страница создания нового теста """

    if not request.user.is_admin:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = EditTestForm(request.POST)
        if form.is_valid():
            test = TestModel(
                name=form.cleaned_data['name'],
                category=form.cleaned_data['category'],
                description=form.cleaned_data['description'],
                author=request.user)
            test.save()
            return HttpResponseRedirect(f'/test/{ test.id }/edit')
    else:
        form = EditTestForm()

    return render(request, 'create_test.html', { 'form': form })


@login_required
def edit_test(request, test_id):
    """ Страница для редактирования теста """

    if not request.user.is_admin:
        return HttpResponseForbidden()

    try:
        test = TestModel.objects.get(id=test_id)
    except TestModel.DoesNotExist:
        return HttpResponseNotFound()

    if request.method == 'POST':
        form = EditTestForm(request.POST)
        if form.is_valid():
            test.name = form.cleaned_data['name']
            test.category = form.cleaned_data['category']
            test.description = form.cleaned_data['description']
            test.save()
    else:
        form = EditTestForm(initial={
            'name': test.name,
            'category': test.category,
            'description': test.description,
        })

    tasks = TaskModel.objects.filter(test=test)
    
    return render(request, 'edit_test.html', { 'form': form, 'test': test, 'tasks': tasks })


@login_required
def edit_test_tasks(request, test_id):
    """ Запрос на изменение задач """

    if not request.user.is_admin:
        return HttpResponseForbidden()
    
    if request.method != 'POST':
        return HttpResponseBadRequest()

    try:
        tasks_data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest()

    try:
        test = TestModel.objects.get(id=test_id)
    except TestModel.DoesNotExist:
        return HttpResponseNotFound()

    tasks = list(TaskModel.objects.filter(test=test))

    if len(tasks_data) < len(tasks):
        for i in range(len(tasks) - len(tasks_data)):
            tasks.pop().delete()

    for i in range(len(tasks)):
        tasks[i].name = tasks_data[i]['name']
        tasks[i].description = tasks_data[i]['description']
        tasks[i].type = tasks_data[i]['type']
        tasks[i].options = json.dumps(tasks_data[i]['options'])
        tasks[i].answers = json.dumps(tasks_data[i]['answers'])
        tasks[i].save()
    
    if len(tasks_data) > len(tasks):
        for i in range(len(tasks_data) - len(tasks)):
            task_data = tasks_data[len(tasks) + i]
            new_task = TaskModel(
                test=test,
                name=task_data['name'],
                description=task_data['description'],
                type=task_data['type'],
                options=json.dumps(task_data['options']),
                answers=json.dumps(task_data['answers']))
            new_task.save()
            tasks.append(new_task)

    return HttpResponse('ok')