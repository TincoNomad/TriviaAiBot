from rest_framework import serializers
from .models import Score, LeaderBoard, TriviaWinner
from api.utils.jwt_utils import get_user_id_by_username
from django.contrib.auth import get_user_model
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LeaderBoardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    
    class Meta:
        model = LeaderBoard
        fields: list[str] = ['id', 'discord_channel', 'username']

    def create(self, validated_data: Dict[str, Any]) -> LeaderBoard:
        discord_channel = validated_data.get('discord_channel')
        username = validated_data.pop('username')
        User = get_user_model()
        
        logger.info(f"Attempting to create/get leaderboard for channel: {discord_channel}, username: {username}")
        
        # Verificar si ya existe el leaderboard
        existing_leaderboard = LeaderBoard.objects.filter(discord_channel=discord_channel).first()
        if existing_leaderboard:
            logger.info(f"Found existing leaderboard for channel: {discord_channel}")
            return existing_leaderboard
            
        try:
            # Buscar el usuario
            user = User.objects.get(username=username)
            logger.info(f"Found user: {username}")
            
            # Crear nuevo leaderboard
            leaderboard = LeaderBoard.objects.create(
                discord_channel=discord_channel,
                created_by=user
            )
            logger.info(f"Created new leaderboard for channel: {discord_channel}")
            return leaderboard
            
        except User.DoesNotExist:
            logger.error(f"User not found: {username}")
            raise serializers.ValidationError({
                "username": "No existe un usuario con este username"
            })
        except Exception as e:
            logger.error(f"Error creating leaderboard: {str(e)}")
            raise serializers.ValidationError({
                "error": f"Error creating leaderboard: {str(e)}"
            })

    def validate_discord_channel(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("El canal de Discord es requerido")
        return value

    def validate_username(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("El username es requerido")
        return value

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