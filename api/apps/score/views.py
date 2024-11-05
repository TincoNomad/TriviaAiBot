# from tkinter.messagebox import NO
# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Score, TriviaWinner
from .serializers import ScoreSerializer, TriviaWinnerSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from api.utils.jwt_utils import auth_jwt

class UpdateScores(APIView):

    def post(self, request, format= None):
        serializer = ScoreSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            points = serializer.validated_data['points']

            if Score.objects.filter(name=name).exists():
                serializer = Score.objects.get(name=name)
                serializer.points =F('points') + points

            serializer.save()

            return Response(None, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LeaderBoard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        user_id = auth_jwt(request)
        if user_id is None:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
        
        scores = Score.objects.all().order_by('-points')[:10]
        serializer = ScoreSerializer(scores, many=True)
        response_data = {
            'leaderboard': serializer.data,
            'current_user_id': user_id
        }
        
        return Response(response_data)

class UserScoreListView(generics.ListAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Score.objects.filter(user=self.request.user)

class TriviaWinnerListCreateView(generics.ListCreateAPIView):
    queryset = TriviaWinner.objects.all()
    serializer_class = TriviaWinnerSerializer
    permission_classes = [IsAuthenticated]

class TriviaWinnerDetailView(generics.RetrieveDestroyAPIView):
    queryset = TriviaWinner.objects.all()
    serializer_class = TriviaWinnerSerializer
    permission_classes = [IsAuthenticated]
