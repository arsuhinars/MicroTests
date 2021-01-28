
let desktopVersionEvent = new Event('desktopVersion')   //События перестройки сайта для настольных систем
let mobileVersionEvent = new Event('mobileVersion')     //События перестройки сайта для мобильных систем

//Словарь содержащий имена всех ошибок
const errorNames = {
    'timeout': 'Превышено время ожидания',
    'error': 'Произошла ошибка',
    'abort': 'Отправка была прервана',
    'parsererror': 'Неправильный формат ответа'
}

//Функция обновления расположения объектов
function updatePage() {
    let footer = $('footer')
    footer.hide()

    let width = $(document).width()
    let height = $(document).height()

    footer.show()

    //Если окно открыто в портретном виде
    if (width <= 870) {
        $('#header-menu').show()
        $('.login-button').hide()
        $('.register-button').hide()
        $('.header-user').hide()
        $('.header-notifications').hide()
        $('.user-menu').hide()
        $('.notifications-menu').hide()
        $('header > ul').hide()
        $('.header-logo').css({
            'float': 'none',
            'margin': '0 auto'
        })
        document.dispatchEvent(mobileVersionEvent)
    }
    else {
        $('header > ul').show()
        $('.login-button').show()
        $('.register-button').show()
        $('.header-user').show()
        $('.header-notifications').show()
        $('#header-menu').hide()
        $('.mobile-menu').hide()
        $('.header-logo').css({
            'float': 'left',
            'margin': '0'
        })
        document.dispatchEvent(desktopVersionEvent)
    }

    //Задаём отступ для подвала, для того чтобы он всегда находился в низу страницы
    let footerOffset = footer.offset()
    let footerHeight = footer.height()
    if (footerOffset.top - footerHeight < height) {
        footer.offset({
            top: height - footerHeight - 2,
            left: footerOffset.left
        })
    }
}

$(window).on('load resize', updatePage)
$(document).ready(function(){
    //При нажатии на мобильное меню
    $('#header-menu').click(() =>
        $('.mobile-menu').slideToggle(300))
    $('.mobile-menu').hide()

    //При нажатии на меню пользователя (на десктопе)
    $('.header-user').click(() =>
        $('.user-menu').slideToggle(200))
    $('.user-menu').hide()

    //При нажатии на меню уведомлений (на десктопе)
    $('.header-notifications').click(() =>
        $('.notifications-menu').slideToggle(200))
    $('.notifications-menu').hide()

    //При нажатии на уведомление
    $('.notifications-menu li').click((event) =>
        $(event.target).find('.unread-notification-circle').remove())

    //При нажатии на пустом месте
    $(document).click((event) => {
        //Закрываем меню, если кликнули мимо
        if ($(event.target).closest('.user-menu, .header-user').length == 0)
            $('.user-menu').slideUp(200)
        if ($(event.target).closest('.header-notifications, .notifications-menu').length == 0)
            $('.notifications-menu').slideUp(200)
        if ($(event.target).closest('#header-menu, .mobile-menu').length == 0)
            $('.mobile-menu').slideUp(200)
    })

    $('form').each((index, form) => {
        //При изменении значения поля сбрасываем его ошибки
        $(form).find('input').focus(function (element) {
            $(form).find('.non-field-errors').empty()
            $(form).find('#' + $(element.target).attr('name') + '_errors').empty()
            $(element.target).css('border-color', '')
            updatePage()
        })
    })
})

//Функция проверки формы на ошибки
function ajaxSubmitForm(form, success, error) {
    let formData = new FormData(form)   //Получаем все данные формы

    //Блокируем все элементы формы
    $(form).find('input').prop('disabled', true)

    //Отправляем AJAX запрос
    $.ajax({
        type: 'POST',
        data: formData,
        dataType: 'json',
        url: $(form).prop('action'),
        processData: false,
        contentType: false,
        success: (data) => {
            let result = true
            let nonFieldErrors = $(form).find('.non-field-errors')
            //Очищаем списки ошибок
            nonFieldErrors.empty()
            $(form).find('.errors-list').empty()
            //Выводим ошибки, если таковые имеются
            for (field in data) {
                for (error of data[field]) {
                    //Если ошибка не относиться к какому-то полю
                    if (field == '__all__')
                        nonFieldErrors.append($('<li>' + error.message + '</li>'))
                    else {
                        $(form).find('#id_' + field).css('border-color', 'red')
                        $(form).find('#' + field + '_errors').append($('<li>' + error.message + '</li>'))
                    }
                    result = false
                }
            }
            //Разблокируем все элементы
            $(form).find('input').prop('disabled', false)
            
            updatePage()
            if (result) if (success) success()
            else if (error) error()
        },
        error: (jqXHR, textStatus, errorThrown) => {
            //Получаем текст ошибки
            let errorText = errorNames[textStatus]
            if (errorThrown) errorText += ': ' + errorThrown

            let nonFieldErrors = $(form).find('.non-field-errors')
            //Очищаем списки ошибок
            nonFieldErrors.empty()
            //Добавляем текст ошибки
            nonFieldErrors.append($('<li>', {text: errorText}))

            //Разблокируем все элементы
            $(form).find('input').prop('disabled', false)

            if (error) error()
        }
    })
}
