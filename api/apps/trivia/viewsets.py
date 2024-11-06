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

class TriviaViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'list':
            return TriviaListSerializer
        return TriviaSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            return []
        if self.action == 'toggle_visibility':
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]
    
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

class ThemeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [permissions.IsAuthenticated]
