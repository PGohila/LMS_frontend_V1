from django.urls import path,include
from .views import *

urlpatterns = [
    path("",login, name="login"),
    path('logout/', logout, name='logout'),
    path("dashboard/",dashboard, name="dashboard"),
    path('user_registration/', user_registration, name='user_registration'),
    path('user_list/', user_list, name='user_list'),
    path('user_edit/<pk>/', user_edit, name='user_edit'),
    path('user_view/<pk>/', user_view, name='user_view'),
    path('user_delete/<pk>/', user_delete, name='user_delete'),
    path('roles/', roles, name='roles'),
    path('roles_create/', roles_create, name='roles_create'),
    path('roles_edit/<pk>/', roles_edit, name='roles_edit'),
    path('roles_delete/<pk>/', roles_delete, name='roles_delete'),
    path('permission/<pk>/', permission, name='permission'),
    path('function_setup/', function_setup, name='function_setup'),
    path('multi_factor_authentication/', multi_factor_authentication, name='multi_factor_authentication'),

    path('userprofile_list/', userprofile_list, name='userprofile_list'),
    path('userprofile_create/', userprofile_create, name='userprofile_create'),
    path('userprofile_edit/<pk>/', userprofile_edit, name='userprofile_edit'),
    path('userprofile_delete/<pk>/', userprofile_delete, name='userprofile_delete'),
]