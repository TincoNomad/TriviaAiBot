from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .apps.trivia.viewsets import TriviaViewSet, ThemeViewSet
from .apps.trivia.views import GetQuestions
from .apps.score.viewsets import ScoreViewSet, TriviaWinnerViewSet, LeaderBoardViewSet
from .apps.users.views import RegisterView, LoginView, LogoutView, CreateUserView, SetupCredentialsView
from .apps.users.viewsets import UserViewSet

router = DefaultRouter()
router.register(r'trivias', TriviaViewSet, basename='trivia')
router.register(r'themes', ThemeViewSet, basename='theme')
router.register(r'score', ScoreViewSet, basename='score')
router.register(r'winners', TriviaWinnerViewSet, basename='winner')
router.register(r'users', UserViewSet, basename='user')
router.register(r'leaderboards', LeaderBoardViewSet, basename='leaderboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/questions/<uuid:trivia_id>/', GetQuestions.as_view(), name='get-questions'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/create-user/', CreateUserView.as_view(), name='create-user'),
    path('api/update-credentials/', SetupCredentialsView.as_view(), name='update-credentials'),
]

#static file management
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)