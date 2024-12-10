from django.contrib import admin
from django.urls import include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .apps.trivia.viewsets import TriviaViewSet, ThemeViewSet
from .apps.score.viewsets import ScoreViewSet, TriviaWinnerViewSet, LeaderBoardViewSet
from .apps.users.views import RegisterView, LoginView, LogoutView, CreateUserView, SetupCredentialsView
from .apps.users.viewsets import UserViewSet

# Configurar el router para que no requiera slash final
class OptionalSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = '/?'

router = OptionalSlashRouter()
router.register(r'trivias', TriviaViewSet, basename='trivia')
router.register(r'themes', ThemeViewSet, basename='theme')
router.register(r'score', ScoreViewSet, basename='score')
router.register(r'winners', TriviaWinnerViewSet, basename='winner')
router.register(r'users', UserViewSet, basename='user')
router.register(r'leaderboards', LeaderBoardViewSet, basename='leaderboard')

urlpatterns = [
    re_path(r'^admin/?', admin.site.urls),
    re_path(r'^api/?', include(router.urls)),
    re_path(r'^api/register/?', RegisterView.as_view(), name='register'),
    re_path(r'^api/login/?', LoginView.as_view(), name='login'),
    re_path(r'^api/logout/?', LogoutView.as_view(), name='logout'),
    re_path(r'^api/create-user/?', CreateUserView.as_view(), name='create-user'),
    re_path(r'^api/update-credentials/?', SetupCredentialsView.as_view(), name='update-credentials'),
]

#static file management
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)