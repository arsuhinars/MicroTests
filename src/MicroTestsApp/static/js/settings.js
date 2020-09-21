
document.addEventListener('desktopVersion', function() {
    $('.block').css('width', '')
    $('.block').css('display', 'flex')
    $('.block, .settings input').css('text-align', '')
    $('.block ul').css('width', '200px')
})

document.addEventListener('mobileVersion', function() {
    $('.block').css('width', '90%')
    $('.block').css('display', 'block')
    $('.block, .settings input').css('text-align', 'center')
    $('.block ul').css('width', '100%')
})

$(document).ready(function() {
    //При изменении аватарки
    $('#id_avatar').change(function (event) {
        let reader = new FileReader()
        reader.onload = function(e) {
            $('.avatar-img').css('background-image', `url(${e.target.result})`)
        }
        reader.readAsDataURL(event.target.files[0])
    })

    //При отправке формы основных настроек
    $('.general-menu form').submit(function(event) {
        event.preventDefault()  //Отменяем отправку формы
        //Проверяем на наличие ошибок
        ajaxSubmitForm(event.target, function() {
            document.location.reload()  //Перезагружаем страницу
        })
    })

    //При отправке формы изменения пароля
    $('.password-menu form').submit(function(event) {
        event.preventDefault()  //Отменяем отправку формы
        //Проверяем на наличие ошибок
        ajaxSubmitForm(event.target, function() {
            //Если форма изменения пароля
            if ($(event.target).hasClass('change_password_form')) {
                $('.change_password_form').fadeOut(300, function() {
                    $('.password-menu .confirm_code_form').fadeIn(300)
                    updatePage()
                })
            }
            //Если форма подверждения кодом
            else if ($(event.target).hasClass('confirm_code_form')) {
                $('.password-menu .confirm_code_form').fadeOut(300, function() {
                    $('.password_confirmed_box').fadeIn(300)
                    updatePage()
                })
            }
        })
    })

    //При отправке формы изменения почты
    $('.email-menu form').submit(function(event) {
        event.preventDefault()  //Отменяем отправку формы
        //Проверяем на наличие ошибок
        ajaxSubmitForm(event.target, function() {
            //Если форма изменения почты
            if ($(event.target).hasClass('change_email_form')) {
                $('.change_email_form').fadeOut(300, function() {
                    $('.email-menu .confirm_code_form').fadeIn(300)
                    updatePage()
                })
            }
            //Если форма подверждения кодом
            else if ($(event.target).hasClass('confirm_code_form')) {
                $('.email-menu .confirm_code_form').fadeOut(300, function() {
                    $('.email_confirmed_box').fadeIn(300)
                    updatePage()
                })
            }
        })
    })

    $('.email-menu, .password-menu').hide()
    $('.confirm_code_form, .password_confirmed_box, .email_confirmed_box').hide()

    //При выборе основных настроек
    let currentMenu = '.general-menu'
    $('.general-button').click(function() {
        if (currentMenu != '.general-menu') {
            $(currentMenu).fadeOut(300, function() {
                currentMenu = '.general-menu'
                $('.email-menu, .password-menu').hide()
                $('.general-menu').fadeIn(300)
                updatePage()
            })
        }
    })
    //При выборе настроек почты
    $('.email-button').click(function() {
        if (currentMenu != '.email-menu') {
            $(currentMenu).fadeOut(300, function() {
                currentMenu = '.email-menu'
                $('.general-menu, .password-menu').hide()
                $('.email-menu').fadeIn(300)
                updatePage()
            })
        }
    })
    //При выборе настроек пароля
    $('.password-button').click(function() {
        if (currentMenu != '.password-menu') {
            $(currentMenu).fadeOut(300, function() {
                currentMenu = '.password-menu'
                $('.general-menu, .email-menu').hide()
                $('.password-menu').fadeIn(300)
                updatePage()
            })
        }
    })
})
