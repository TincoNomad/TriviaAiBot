from django.contrib import admin
from django.urls import path
from .trivia.views import RandomQuestions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/random/',RandomQuestions.as_view(), name='random')
]
