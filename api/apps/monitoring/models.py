from django.db import models
from django.utils import timezone

# Create your models here.

class RequestLog(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    response_time = models.FloatField()
    status_code = models.IntegerField()
    user_id = models.IntegerField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['path']),
            models.Index(fields=['status_code'])
        ]
        
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code}"

class ErrorLog(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    error_type = models.CharField(max_length=100)
    error_message = models.TextField()
    traceback = models.TextField()
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    user_id = models.IntegerField(null=True)
    request_data = models.JSONField(null=True, blank=True)
    url = models.URLField(max_length=255)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['error_type'])
        ]
