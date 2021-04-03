from django.urls import path

from .views import *

urlpatterns = [
    path('', index),
    path('authorization/', authorization),
    path('register/', register),
    path('login/', login),
    path('notifications/', notifications),
    path('settings/', settings),
    path('logout/', logout_view),
    path('notification/<int:id>', notification),
    path('tests_list/', tests_list),
    path('test/<int:test_id>', test_view),
    path('test/<int:test_id>/task/<int:task_index>', task_view),
    path('test/<int:test_id>/results/', results),
    path('test/<int:test_id>/all_results/<int:page>', all_results),
    path('test/<int:test_id>/edit', edit_test),
    path('test/<int:test_id>/edit_tasks', edit_test_tasks),
    path('save_result/', save_result),
    path('create_test/', create_test),
]
