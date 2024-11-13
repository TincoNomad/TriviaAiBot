from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from .serializers import TriviaSerializer
from .models import Trivia
from api.utils.logging_utils import log_exception, logger
from django.shortcuts import get_object_or_404
from uuid import UUID

class GetQuestions(APIView):
    permission_classes: list[BasePermission] = []
    
    @log_exception
    def get(self, request, trivia_id: UUID, format=None):
        try:
            trivia = get_object_or_404(Trivia, id=trivia_id, is_public=True)
            serializer_trivia = TriviaSerializer(trivia)
            questions = serializer_trivia.data.get('questions', [])
            logger.info(f"Retrieved questions for trivia ID: {trivia_id}")
            return Response(questions)
        except Exception as e:
            logger.error(f"Error retrieving questions for trivia {trivia_id}: {str(e)}")
            raise
