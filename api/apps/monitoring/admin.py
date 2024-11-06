from django.contrib import admin
from .models import RequestLog, ErrorLog

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'method', 'path', 'status_code', 'response_time', 'user_id']
    list_filter = ['method', 'status_code', 'timestamp']
    search_fields = ['path', 'user_id']
    readonly_fields = ['timestamp', 'method', 'path', 'status_code', 'response_time', 
                      'user_id', 'ip_address', 'request_data', 'response_data']

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'error_type', 'method', 'path', 'user_id']
    list_filter = ['error_type', 'method', 'timestamp']
    search_fields = ['path', 'error_message', 'user_id']
    readonly_fields = ['timestamp', 'error_type', 'error_message', 'traceback', 
                      'path', 'method', 'user_id', 'request_data', 'url']
