from django import template

register = template.Library()

@register.simple_tag
def add_css_class_for_label(obj, **kwargs):
    """ Фильтр, позволяющий добавить css классы для заголовка формы """
    return obj.label_tag(attrs=kwargs)
