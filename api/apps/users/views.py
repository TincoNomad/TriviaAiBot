from rest_framework import generics, permissions, status, views
from rest_framework.response import Response 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from utils.jwt_utils import IsAdminUser

# Create your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
class LoginView(TokenObtainPairView):
    pass

class RefreshTokenView(TokenRefreshView):
    pass

class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
