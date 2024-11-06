from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from api.apps.monitoring.models import RequestLog, ErrorLog

class Command(BaseCommand):
    help = 'Cleanup old logs based on retention settings'

    def handle(self, *args, **options):
        request_retention = settings.MONITORING['REQUEST_LOG_RETENTION_DAYS']
        error_retention = settings.MONITORING['ERROR_LOG_RETENTION_DAYS']
        
        request_threshold = timezone.now() - timedelta(days=request_retention)
        error_threshold = timezone.now() - timedelta(days=error_retention)
        
        # Borrar logs por lotes para evitar sobrecarga de memoria
        batch_size = 1000
        
        # Borrar request logs
        deleted_requests = 0
        while RequestLog.objects.filter(timestamp__lt=request_threshold).exists():
            ids = RequestLog.objects.filter(
                timestamp__lt=request_threshold
            ).values_list('id', flat=True)[:batch_size]
            deleted_count, _ = RequestLog.objects.filter(id__in=list(ids)).delete()
            deleted_requests += deleted_count
            
        # Borrar error logs
        deleted_errors = 0
        while ErrorLog.objects.filter(timestamp__lt=error_threshold).exists():
            ids = ErrorLog.objects.filter(
                timestamp__lt=error_threshold
            ).values_list('id', flat=True)[:batch_size]
            deleted_count, _ = ErrorLog.objects.filter(id__in=list(ids)).delete()
            deleted_errors += deleted_count
            
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted_requests} request logs and {deleted_errors} error logs'
            )
        )
