from asyncio.log import logger
import time
import json
from .models import RequestLog, ErrorLog
from django.utils import timezone
from api.utils.logging_utils import log_exception

class MonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    @log_exception
    def __call__(self, request):
        start_time = time.time()
        
        try:
            request_data = json.loads(request.body) if request.body else None
        except json.JSONDecodeError:
            request_data = None
        
        response = self.get_response(request)
        
        try:
            response_data = json.loads(response.content) if response.content else None
        except json.JSONDecodeError:
            response_data = None
        
        duration = time.time() - start_time
        
        try:
            if response.status_code >= 400:
                ErrorLog.objects.create(
                    error_type=str(response.status_code),
                    error_message=getattr(response, 'reason_phrase', 'Unknown'),
                    path=request.path,
                    method=request.method,
                    user_id=getattr(request.user, 'id', None) if request.user.is_authenticated else None,
                    request_data=request_data,
                    url=request.build_absolute_uri()
                )
            else:
                RequestLog.objects.create(
                    path=request.path,
                    method=request.method,
                    response_time=duration,
                    status_code=response.status_code,
                    user_id=getattr(request.user, 'id', None) if request.user.is_authenticated else None,
                    ip_address=self.get_client_ip(request),
                    request_data=request_data,
                    response_data=response_data
                )
        except Exception as e:
            # Si falla el logging, no interrumpimos la respuesta
            logger.error(f"Error en MonitoringMiddleware: {str(e)}")
            
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
