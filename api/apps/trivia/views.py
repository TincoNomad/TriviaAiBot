from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from .serializers import TriviaSerializer
from .models import Trivia
from api.utils.logging_utils import log_exception, logger

class RandomQuestions(APIView):
    permission_classes: list[BasePermission] = []
    
    @log_exception
    def get(self, request, format=None, **kwargs):
        try:
            trivia = Trivia.objects.filter(is_public=True).order_by('?')[:1]
            serializer_trivia = TriviaSerializer(trivia, many=True)
            logger.info("Random trivia questions retrieved successfully")
            return Response(serializer_trivia.data)
        except Exception as e:
            logger.error(f"Error retrieving random questions: {str(e)}")
            raise
