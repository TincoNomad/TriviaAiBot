from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import F
from .models import Score, TriviaWinner, LeaderBoard
from .serializers import ScoreSerializer, LeaderBoardSerializer, TriviaWinnerSerializer
from api.utils.logging_utils import log_exception, logger

class LeaderBoardViewSet(viewsets.ModelViewSet):
    serializer_class = LeaderBoardSerializer

    def get_queryset(self):
        return LeaderBoard.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Leaderboard created successfully',
                'id': serializer.instance.id,
                'discord_channel': serializer.instance.discord_channel
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScoreViewSet(viewsets.GenericViewSet):
    serializer_class = ScoreSerializer

    @log_exception
    def get_queryset(self):
        return Score.objects.all()

    @log_exception
    @action(detail=False, methods=['post'])
    def update_score(self, request):
        """
        Creates or updates a score for a specific leaderboard.
        Se puede identificar el leaderboard por id o por discord_channel.
        
        POST /api/scores/update_score/
        {
            "name": "Player1",
            "points": 50,
            "leaderboard_id": "550e8400-e29b-41d4-a716-446655440000"
        }
        
        o
        
        {
            "name": "Player1",
            "points": 50,
            "discord_channel": "My Channel"
        }
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                name = serializer.validated_data['name']
                points = serializer.validated_data['points']
                
                # Obtener leaderboard por ID o discord_channel
                leaderboard_id = request.data.get('leaderboard_id')
                discord_channel = request.data.get('discord_channel')
                
                if not leaderboard_id and not discord_channel:
                    return Response(
                        {"error": "Either leaderboard_id or discord_channel must be provided"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    if leaderboard_id:
                        leaderboard = LeaderBoard.objects.get(id=leaderboard_id)
                    else:
                        leaderboard = LeaderBoard.objects.get(discord_channel=discord_channel)
                except LeaderBoard.DoesNotExist:
                    return Response(
                        {"error": "LeaderBoard not found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )

                logger.info(f"Updating score for {name} in leaderboard {leaderboard.discord_channel}")
                
                score, created = Score.objects.get_or_create(
                    name=name,
                    leaderboard=leaderboard,
                    defaults={'points': points}
                )
                
                if not created:
                    score.points = F('points') + points
                    score.save()

                score.refresh_from_db()

                return Response({
                    'message': 'Score updated successfully',
                    'created': created,
                    'name': score.name,
                    'points': score.points,
                    'leaderboard_id': str(leaderboard.id),
                    'discord_channel': leaderboard.discord_channel
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating score: {str(e)}")
            raise

    @log_exception
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """
        Gets the top 10 scores for a specific leaderboard.
        GET /api/scores/leaderboard/{leaderboard_id}/
        """
        try:
            leaderboard = LeaderBoard.objects.get(pk=pk)
            scores = Score.objects.filter(leaderboard=leaderboard).order_by('-points')[:10]
            serializer = self.get_serializer(scores, many=True)
            
            return Response({
                'leaderboard_name': leaderboard.name,
                'created_by': str(leaderboard.created_by.id),
                'scores': serializer.data
            })
        except LeaderBoard.DoesNotExist:
            return Response(
                {"error": "LeaderBoard not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving leaderboard: {str(e)}")
            raise

class TriviaWinnerViewSet(viewsets.ModelViewSet):
    queryset = TriviaWinner.objects.all()
    serializer_class = TriviaWinnerSerializer
