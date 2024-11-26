from django.urls import path,include
from .views import *
from django.contrib.auth import views as auth_views


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
    path('userprofile_edit/<id>/', userprofile_edit, name='userprofile_edit'),
    path('userprofile_delete/<id>/', userprofile_delete, name='userprofile_delete'),
    
    path('change_password/', change_password, name='change_password'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('set_password/<email>', set_password, name='set_password'),

    # path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    # path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

]