from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from .apps.trivia.views import RandomQuestions, TriviaListCreateView, TriviaDetailView, ThemeListView
from .apps.score.views import UpdateScores, LeaderBoard, UserScoreListView, TriviaWinnerListCreateView, TriviaWinnerDetailView
from .apps.users.views import RegisterView, LoginView, LogoutView
from django.conf import settings # type: ignore
from django.conf.urls.static import static # type: ignore


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/random-question/', RandomQuestions.as_view(), name='random-question'),
    path('api/score/', UpdateScores.as_view(), name='score-update'),
    path('api/leaderboard/', LeaderBoard.as_view(), name='leaderboard'), 
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/themes/', ThemeListView.as_view(), name='theme-list'),
    path('api/trivias/', TriviaListCreateView.as_view(), name='trivia-list-create'),
    path('api/trivias/<int:pk>/', TriviaDetailView.as_view(), name='trivia-detail'),
    path('api/user-scores/', UserScoreListView.as_view(), name='user-score-list'),
    path('api/trivia-winners/', TriviaWinnerListCreateView.as_view(), name='trivia-winner-list-create'),
    path('api/trivia-winners/<int:pk>/', TriviaWinnerDetailView.as_view(), name='trivia-winner-detail'),
]

#static file management
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
