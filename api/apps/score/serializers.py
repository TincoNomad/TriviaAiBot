from rest_framework import serializers
from .models import Score, LeaderBoard, TriviaWinner
from api.utils.jwt_utils import get_user_id_by_username

class LeaderBoardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    
    class Meta:
        model = LeaderBoard
        fields = ['id', 'discord_channel', 'created_by', 'created_at', 'username']
        read_only_fields = ['created_by', 'created_at']

    def validate(self, data):
        username = data.get('username')
        user_id = get_user_id_by_username(username)
        if not user_id:
            raise serializers.ValidationError({
                "username": "No existe un usuario con este username"
            })
        return data

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['id', 'name', 'points', 'leaderboard', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']

class TriviaWinnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriviaWinner
        fields = ['id', 'name', 'trivia_name', 'score', 'date_won']
        read_only_fields = ['date_won']