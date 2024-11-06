import time
import json
from .models import RequestLog, ErrorLog
from django.utils import timezone

class MonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Capturar request data
        try:
            request_data = json.loads(request.body) if request.body else None
        except json.JSONDecodeError:
            request_data = None
        
        response = self.get_response(request)
        
        # Capturar response data
        try:
            response_data = json.loads(response.content) if response.content else None
        except json.JSONDecodeError:
            response_data = None
        
        duration = time.time() - start_time
        
        # Log request
        if response.status_code >= 400:
            # Log error
            ErrorLog.objects.create(
                error_type=str(response.status_code),
                error_message=getattr(response, 'reason_phrase', 'Unknown'),
                path=request.path,
                method=request.method,
                user_id=request.user.id if request.user.is_authenticated else None,
                request_data=request_data,
                url=request.build_absolute_uri()
            )
        else:
            # Log successful request
            RequestLog.objects.create(
                path=request.path,
                method=request.method,
                response_time=duration,
                status_code=response.status_code,
                user_id=request.user.id if request.user.is_authenticated else None,
                ip_address=self.get_client_ip(request),
                request_data=request_data,
                response_data=response_data
            )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
