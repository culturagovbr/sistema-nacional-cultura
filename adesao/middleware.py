from threading import local

_thread_locals = local()

class ThreadLocalUserMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response

def get_current_user():
    request = getattr(_thread_locals, "request", None)
    try:
        user = request.user.usuario
    except AttributeError:
        user = None

    return user
