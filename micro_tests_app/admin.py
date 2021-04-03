from django.contrib import admin

from .models import *

class NotificationInline(admin.StackedInline):
    model = Notification
    fields = ('title', 'url', 'user', 'has_been_read')
    readonly_fields = ('user', 'has_been_read')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ( 'email', 'last_name', 'first_name', 'last_login', 'date_joined', 'is_active', 'is_admin' )
    list_filter = ( 'date_joined', 'last_login', 'is_active', 'is_admin' )
    fields = ( 'email', 'last_name', 'first_name', 'last_login', 'date_joined', 'is_active', 'is_admin' )
    readonly_fields = ( 'last_login', 'date_joined' )
    inlines = [NotificationInline]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'title', 'send_time', 'has_been_read' )
    list_filter = ( 'send_time', )
    fields = ( 'title', 'url', 'user', 'send_time', 'has_been_read' )
    readonly_fields = ( 'user', 'send_time', 'has_been_read' )


@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):
    list_display = ( 'category', 'name', 'publish_date', 'author' )
    list_filter = ( 'category', 'publish_date', )
    fields = ( 'category', 'name', 'publish_date', 'author', 'description'  )
    readonly_fields = ( 'publish_date', )


@admin.register(TaskModel)
class TaskModelAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'test', 'type' )
    fields = ( 'name', 'test', 'type', 'description', 'options', 'answers' )


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ( 'user', 'test', 'points', 'save_time' )
    fields = ( 'user', 'test', 'points', 'tasks_amount', 'save_time' )
    readonly_fields = ( 'save_time', 'tasks_amount', 'points', 'test', 'user' )
