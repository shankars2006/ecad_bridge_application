# blog/decorators.py

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """
    Allows access only to logged-in staff users.
    Redirects unauthenticated users to login page.
    Raises 403 for non-admin logged-in users.
    """

    @login_required(login_url='/login/')
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped_view
