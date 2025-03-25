# floodless/middleware.py
from django.http import HttpResponseRedirect
from django.urls import reverse

class RedirectRootToHomeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/':
            return HttpResponseRedirect(reverse('home'))
        return self.get_response(request)