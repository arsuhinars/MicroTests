from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ( 'email', 'last_name', 'first_name', 'last_login', 'date_joined' )
    list_filter = ( 'date_joined', 'last_login' )
    fields = ( 'avatar', 'last_name', 'first_name', 'is_confirmed', 'is_active', 'is_admin' )

# Регистрируем модели для панели администратора
admin.site.register(User, UserAdmin)
