# middleware.py

from django.conf import settings
from django.http import HttpResponse
from django.template import loader


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE:
            template = loader.get_template('maintenance.html')
            return HttpResponse(template.render({}, request))

        response = self.get_response(request)
        return response
