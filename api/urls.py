from django.contrib import admin
from django.urls import path
from .apps.trivia.views import RandomQuestions
from .apps.score.views import UpdateScores, LeaderBoard
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin', admin.site.urls),
    path('api/question',RandomQuestions.as_view(), name='question'),
    path('api/score',UpdateScores.as_view(), name='score_update'),
    path('api/score/leaderboard', LeaderBoard.as_view(), name='leaderboard'), 
]

#static file management
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)