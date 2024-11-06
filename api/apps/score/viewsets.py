from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from .models import Score, TriviaWinner
from .serializers import ScoreSerializer, TriviaWinnerSerializer
from rest_framework.permissions import IsAuthenticated
from api.utils.jwt_utils import auth_jwt
from api.utils.logging_utils import log_exception, logger

class ScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated]

    @log_exception
    def get_queryset(self):
        return Score.objects.filter(user=self.request.user)
    
    @log_exception
    @action(detail=False, methods=['post'])
    def update_score(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                name = serializer.validated_data['name']
                points = serializer.validated_data['points']
                logger.info(f"Updating score for {name}: +{points} points")
                
                if Score.objects.filter(name=name).exists():
                    score = Score.objects.get(name=name)
                    score.points = F('points') + points
                    score.save()
                else:
                    serializer.save(user=request.user)

                return Response(None, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating score: {str(e)}")
            raise

    @log_exception
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        try:
            user_id = auth_jwt(request)
            if user_id is None:
                logger.warning("Invalid token in leaderboard request")
                return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            
            scores = Score.objects.all().order_by('-points')[:10]
            serializer = self.get_serializer(scores, many=True)
            logger.info("Leaderboard retrieved successfully")
            return Response({
                'leaderboard': serializer.data,
                'current_user_id': user_id
            })
        except Exception as e:
            logger.error(f"Error retrieving leaderboard: {str(e)}")
            raise

class TriviaWinnerViewSet(viewsets.ModelViewSet):
    queryset = TriviaWinner.objects.all()
    serializer_class = TriviaWinnerSerializer
    permission_classes = [IsAuthenticated]
