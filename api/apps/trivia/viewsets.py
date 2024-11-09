from rest_framework import viewsets, permissions
from django.db import models
from .models import Trivia, Theme
from .serializers import TriviaSerializer, ThemeSerializer, TriviaListSerializer
from api.utils.jwt_utils import IsAdminUser
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError as DRFValidationError
from api.utils.logging_utils import log_exception, logger
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from api.utils.jwt_utils import get_user_from_token

class TriviaViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'list':
            return TriviaListSerializer
        return TriviaSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'toggle_visibility']:
            return [permissions.IsAuthenticated()]
        if self.action == 'create':
            return [IsAdminUser()]
        return []
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Trivia.objects.filter(is_public=True)
        if user.role == 'admin':
            return Trivia.objects.all()
        return Trivia.objects.filter(
            models.Q(is_public=True) | 
            models.Q(user=user.created_by)
        )
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(is_public=True)
    
    @action(detail=True, methods=['post'])
    def toggle_visibility(self, request, pk=None):
        trivia = self.get_object()
        
        if not request.user.is_authenticated:
            return Response(
                {"error": "You must be authenticated to change visibility"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if trivia.user != request.user:
            return Response(
                {"error": "Only the authenticated owner can modify visibility"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        trivia.is_public = not trivia.is_public
        trivia.save()
        
        return Response({
            "message": "Visibility updated successfully",
            "is_public": trivia.is_public
        })
    
    @log_exception
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in trivia creation: {e}")
            raise DRFValidationError(detail=str(e))
        except IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            raise DRFValidationError(detail="Could not create trivia due to database constraints")
    
    @action(detail=False, methods=['get'], url_path='filter', authentication_classes=[], permission_classes=[])
    def filter_trivias(self, request):
        theme = request.query_params.get('theme')
        difficulty = request.query_params.get('difficulty')
        
        logger.info(f"Filtering trivias with theme={theme} and difficulty={difficulty}")
        
        if not theme or not difficulty:
            return Response(
                {"error": "The parameters 'theme' and 'difficulty' are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            difficulty = int(difficulty)
            # Base query para trivias públicas
            query = models.Q(theme=theme, difficulty=difficulty, is_public=True)
            
            # Si hay token de autorización, intentar incluir trivias privadas
            # auth_header = request.headers.get('Authorization')
            # if auth_header and auth_header.startswith('Bearer '):
            #     try:
            #         token = auth_header.split(' ')[1]
            #         user = get_user_from_token(token)
            #         if user:
            #             query |= models.Q(theme=theme, difficulty=difficulty, user=user)
            #     except Exception as auth_error:
            #         logger.warning(f"Error processing auth token: {auth_error}")
            #         # Continuar solo con trivias públicas si hay error de autenticación
            #         pass
            
            filtered_trivias = Trivia.objects.filter(query)
            logger.info(f"Found {filtered_trivias.count()} matching trivias")
            
            serializer = self.get_serializer(filtered_trivias, many=True)
            return Response(serializer.data)
            
        except ValueError:
            return Response(
                {"error": "The 'difficulty' parameter must be a number"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error filtering trivias: {e}")
            return Response(
                {"error": "Error filtering trivias"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def difficulty(self, request):
        """Returns the available difficulty options"""
        try:
            difficulties = dict(Trivia.DIFFICULTY_CHOICES)
            return Response(difficulties, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting difficulty choices: {e}")
            return Response(
                {"error": "Error retrieving difficulty choices"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ThemeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
