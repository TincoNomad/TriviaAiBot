from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import ScoreSerializer
from rest_framework.response import Response
from rest_framework import status

from .models import Score

class UpdateScores(APIView):

    def post(self, request, formats=None):
        serializer = ScoreSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            points = serializer.validated_data['points']

            if Score.objects.filter(name=name).exist():
                serializer = Score.objects.get(name=name)
                serializer.points =F('points') + points

            serializer.save()

            return Response(None, status=status.HTMP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTMP_400_BAD_REQUEST)