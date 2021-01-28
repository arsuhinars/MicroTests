from django.contrib import admin
from .models import User, Notification, TestModel

class NotificationAdminInline(admin.TabularInline):
    model = Notification

class UserAdmin(admin.ModelAdmin):
    list_display = ( 'email', 'last_name', 'first_name', 'last_login', 'date_joined' )
    list_filter = ( 'date_joined', 'last_login' )
    fields = ( 'avatar', 'email', 'last_name', 'first_name', 'is_confirmed', 'is_active', 'is_admin' )
    inlines = (
        NotificationAdminInline,
    )

class NotificationAdmin(admin.ModelAdmin):
    list_display = ( 'text', 'receiving_user', 'is_read', 'send_date' )
    list_filter = ( 'send_date', )
    fields = ( 'text', 'is_read' )

# Регистрируем модели для панели администратора
admin.site.register(User, UserAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(TestModel)
