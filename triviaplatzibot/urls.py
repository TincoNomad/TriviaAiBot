#from ast import pattern
from django.contrib import admin
from django.urls import path
from .trivia.views import RandomQuestions
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/random/',RandomQuestions.as_view(), name='random'),
    path(r'^static/(?P.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
]

#urlpatterns += pattern('', (r'^static/(?P.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),)