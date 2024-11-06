from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from api.utils.jwt_utils import IsAdminUser
from api.utils.logging_utils import log_exception, logger
from .models import CustomUser

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    
    def get_permissions(self):
        # Si no hay usuarios, permitir registro sin autenticación
        if not CustomUser.objects.exists():
            return []
        # Si hay usuarios, requerir admin
        return [permissions.IsAuthenticated(), IsAdminUser()]

    def perform_create(self, serializer):
        try:
            # Si es el primer usuario, asignar rol de admin
            if not CustomUser.objects.exists():
                user = serializer.save(role='admin')
            else:
                # Si es creado por un admin, usar el rol especificado
                user = serializer.save(created_by=self.request.user)
            logger.info(f"New user created: {user.username} with role: {user.role}")
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
