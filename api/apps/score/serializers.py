from rest_framework import serializers
from .models import Score, LeaderBoard, TriviaWinner

class LeaderBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderBoard
        fields = ['id', 'discord_channel', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']

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