from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.shortcuts import render,redirect

def users_permission(request):
    try:
        permission = request.session.get('permission')
        # print('permission',permission)
        if permission:
            # print('permission_context_processors', permission)
            return {'permission_user': permission}
        else:
            # logout(request)
            return {}
    except KeyError:
        # If the session key doesn't exist, log out and redirect
        logout(request)
        return {}