from django.http import HttpResponseForbidden

def role_required(required_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user = getattr(request.user, 'user', None)
            if user and user.role in required_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped_view
    return decorator
