# your_app/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def check_permission(permission_codename):
    """
    Custom decorator to check if the user has a specific permission.
    
    :param permission_codename: The codename of the permission to check (e.g., 'app_name.permission_codename').
    """
    def decorator(view_func):
        @wraps(view_func)  # This helps to keep the original view function's metadata
        @login_required    # Ensures that the user is logged in before checking permissions
        def _wrapped_view(request, *args, **kwargs):
            # Check if the user has the required permission
            if request.user.is_superuser or request.user.roles.permissions.filter(function_name=permission_codename):
                # If the user has the permission, call the original view
                return view_func(request, *args, **kwargs)
            else:
                # If the user does not have permission, raise PermissionDenied
                return render(request,'404.html')

        return _wrapped_view

    return decorator
