from django import template

register = template.Library()

@register.simple_tag
def add_attrs_for_label(obj, **kwargs):
    """ Фильтр, позволяющий добавить html атрибуты для заголовка формы """
    return obj.label_tag(attrs=kwargs)


@register.simple_tag
def add_attrs_for_field(obj, **kwargs):
    """ Фильтр, позволяющий добавить html атрибуты полей формы """
    return obj.as_widget(attrs=kwargs)
