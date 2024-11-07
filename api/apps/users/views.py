from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from api.utils.logging_utils import log_exception, logger
from api.utils.jwt_utils import IsAdminUser

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        try:
            user = serializer.save(role='admin')
            logger.info(f"New user registered: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

class LoginView(TokenObtainPairView):
    @log_exception
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"User logged in: {request.data.get('username')}")
            return response
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise

class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @log_exception
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User logged out: {request.user.username}")
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def perform_create(self, serializer):
        try:
            requested_role = self.request.data.get('role', 'user')
            if requested_role not in ['user', 'admin']:
                requested_role = 'user'
            user = serializer.save(role=requested_role, created_by=self.request.user)
            logger.info(f"Admin {self.request.user.username} created new {requested_role}: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
