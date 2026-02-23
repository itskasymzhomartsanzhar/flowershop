from django.conf import settings
from django.http import JsonResponse
from .webapp_auth import WebAppAuth, AuthError
from urllib.parse import unquote

class TelegramDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_handler = WebAppAuth(settings.BOT_TOKEN) #DATACHANGE

    def __call__(self, request):
        init_data = request.headers.get('InitData')
        
        if init_data:
            try:
                init_data = str(init_data)
                output_string = unquote(init_data)
                user_data = self.auth_handler.get_user_data(output_string)
                request.tg_user_data = user_data
            except AuthError as e:
                return JsonResponse({'error': e.message}, status=e.status)
        else:
            request.tg_user_data = 'No any init data'
        response = self.get_response(request)
        return response
 
