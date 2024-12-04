from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

class Command(BaseCommand):
    help = 'Shows all available URLs in the application, separated by type'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\nDefault Django URLs:'))
        self.stdout.write(self.style.SUCCESS('------------------------'))
        self._list_urls(get_resolver(), url_type='django')
        
        self.stdout.write(self.style.SUCCESS('\nAPI URLs (JSON format):'))
        self.stdout.write(self.style.SUCCESS('------------------------'))
        self._list_urls(get_resolver(), url_type='api')
        
        self.stdout.write(self.style.SUCCESS('\nURLs with specific format:'))
        self.stdout.write(self.style.SUCCESS('---------------------------'))
        self._list_urls(get_resolver(), url_type='format')

    def _list_urls(self, resolver, prefix='', url_type='django'):
        seen_urls = set()
        
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLResolver):
                self._list_urls(pattern, prefix=prefix + str(pattern.pattern), url_type=url_type)
            elif isinstance(pattern, URLPattern):
                url = prefix + str(pattern.pattern)
                
                # Avoid duplicate URLs
                if url in seen_urls:
                    continue
                
                # Classify URLs by type
                is_django = url.startswith('admin/') or url.startswith('static/')
                is_format = '.(?P<format>' in url
                is_api = url.startswith('api/') and not is_format
                
                should_display = (
                    (url_type == 'django' and is_django) or
                    (url_type == 'api' and is_api) or
                    (url_type == 'format' and is_format)
                )
                
                if should_display:
                    name = f"[name='{pattern.name}']"
                    view_name = pattern.callback.__name__ if hasattr(pattern.callback, '__name__') else str(pattern.callback)
                    
                    formatted_url = self.style.HTTP_SUCCESS(f"  {url}")
                    formatted_view = self.style.WARNING(f" -> {view_name}")
                    formatted_name = self.style.HTTP_INFO(name)
                    
                    self.stdout.write(f"{formatted_url}{formatted_view} {formatted_name}")
                    seen_urls.add(url)
