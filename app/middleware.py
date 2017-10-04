from django.shortcuts import redirect, reverse

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class SimpleMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated:
            if not request.user.confirm_bool and request.path[:5] != '/auth':
                return redirect(reverse('auth:unconfirmed'))
