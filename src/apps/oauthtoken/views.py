from django.http import HttpResponse
from django.views.generic import View


class OAuth2CallbackView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Autenticación exitosa", content_type="text/plain")
