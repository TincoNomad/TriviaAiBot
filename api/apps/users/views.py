from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, SetupCredentialsSerializer
from api.utils.logging_utils import log_exception, logger
# from api.utils.jwt_utils import IsAdminUser
from rest_framework.views import APIView
from api.apps.users.models import CustomUser

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
            # Verificar si el usuario existe y tiene contraseña
            username = request.data.get('username')
            user = CustomUser.objects.filter(username=username).first()
            
            if user and not user.password:
                return Response(
                    {"detail": "Este usuario no tiene contraseña configurada"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            response = super().post(request, *args, **kwargs)
            logger.info(f"User logged in: {username}")
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

class CreateUserView(APIView):
    def post(self, request):
        data = {
            'username': request.data.get('username'),
            'role': 'user'
        }
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Usuario creado exitosamente',
                'id': user.id,
                'username': user.username,
                'status': 'PENDING_SETUP'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetupCredentialsView(APIView):

    @log_exception
    def post(self, request):
        try:
            serializer = SetupCredentialsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = CustomUser.objects.get(username=request.data['username'])
            result = serializer.update(user, serializer.validated_data)

            return Response({
                'message': 'Credenciales configuradas correctamente',
                'refresh': result['refresh'],
                'access': result['access'],
            })
        except CustomUser.DoesNotExist:
            return Response(
                {'detail': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error configurando credenciales: {str(e)}")
            raise
