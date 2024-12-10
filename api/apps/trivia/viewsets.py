from rest_framework import viewsets, permissions
from django.db import models
from .models import Trivia, Theme, Question, Answer
from .serializers import TriviaSerializer, ThemeSerializer, TriviaListSerializer
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError as DRFValidationError
from api.utils.logging_utils import log_exception, logger
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from api.utils.jwt_utils import get_user_id_by_username


User = get_user_model()

class TriviaViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'list':
            return TriviaListSerializer
        return TriviaSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
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
        # Get username from validated data
        username = serializer.validated_data.get('username')
        user = User.objects.get(username=username)
        
        if user:
            serializer.save(created_by=user, is_public=True)
        else:
            raise ValidationError("User not found")
    
    @action(detail=False, methods=['get'])
    def get_trivia(self, request):
        """
        GET /api/trivias/get_trivia/?id=uuid-de-trivia
        Returns: Detailed information of a specific trivia
        """
        trivia_id = request.query_params.get('id')
        if not trivia_id:
            return Response(
                {"error": "id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            trivia = Trivia.objects.get(id=trivia_id)
            serializer = TriviaSerializer(trivia)
            return Response(serializer.data)
        except Trivia.DoesNotExist:
            return Response(
                {"error": "Trivia not found"},
                status=status.HTTP_404_NOT_FOUND
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
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/trivias/?username=discord_user
        Returns: List of trivias created by the specified user or all public trivias if no username
        """
        username = request.query_params.get('username')
        
        if username:
            try:
                user_id = get_user_id_by_username(username)
                if not user_id:
                    return Response(
                        {"error": f"No se encontró usuario con username: {username}"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                trivias = Trivia.objects.filter(created_by_id=user_id)
                serializer = TriviaListSerializer(trivias, many=True)
                return Response(serializer.data)
                
            except Exception as e:
                logger.error(f"Error al obtener trivias por usuario: {str(e)}")
                return Response(
                    {"error": "Error interno del servidor"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Si no hay username, retorna el comportamiento normal (trivias públicas)
        return super().list(request, *args, **kwargs)
    
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
            query = models.Q(theme=theme, difficulty=difficulty, is_public=True)
            
            filtered_trivias = Trivia.objects.filter(query).values('id', 'title')
            logger.info(f"Found {len(filtered_trivias)} matching trivias")
            
            # Formatear la respuesta como una lista de diccionarios
            simplified_response = [
                {"id": str(trivia['id']), "title": trivia['title']} 
                for trivia in filtered_trivias
            ]
            
            return Response(simplified_response)
            
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
    
    @log_exception
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in trivia creation: {e}")
            raise DRFValidationError(detail=str(e))
        except IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            if 'unique_trivia_title' in str(e):
                raise DRFValidationError(
                    detail="A trivia with this title already exists. Please choose another title."
                )
            raise DRFValidationError(detail="Could not create trivia due to database constraints")
    
    @action(detail=True, methods=['patch'])
    def update_questions(self, request, pk=None):
        """
        PATCH /api/trivias/{trivia_id}/update_questions/
        Updates only questions and answers for a trivia
        """
        try:
            trivia = self.get_object()
            questions_data = request.data.get('questions', [])
            
            # Update questions
            for question_data in questions_data:
                question_id = question_data.get('id')
                if question_id:
                    question = Question.objects.get(id=question_id, trivia=trivia)
                    # Update question fields
                    for key, value in question_data.items():
                        if key != 'answers':
                            setattr(question, key, value)
                    question.save()
                    
                    # Update answers if provided
                    if 'answers' in question_data:
                        for answer_data in question_data['answers']:
                            answer_id = answer_data.get('id')
                            if answer_id:
                                answer = Answer.objects.get(id=answer_id, question=question)
                                for key, value in answer_data.items():
                                    setattr(answer, key, value)
                                answer.save()
            
            return Response({'status': 'questions updated'})
        except Question.DoesNotExist:
            return Response(
                {'error': 'Question not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Answer.DoesNotExist:
            return Response(
                {'error': 'Answer not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating questions: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ThemeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
