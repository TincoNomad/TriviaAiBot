from rest_framework import serializers
from .models import Score, TriviaWinner

class ScoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Score
        fields = [
            'name',
            'points',
        ]

class TriviaWinnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriviaWinner
        fields = ['id', 'name', 'trivia_name', 'date_won', 'score']
        read_only_fields = ['date_won']