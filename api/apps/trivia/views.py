from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from .serializers import TriviaSerializer, ThemeSerializer
from .models import Trivia, Theme
from api.utils.jwt_utils import IsAdminUser
from django.db import models
from rest_framework.permissions import BasePermission

class ThemeListView(generics.ListAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [permissions.IsAuthenticated]

class RandomQuestions(APIView):
    permission_classes: list[BasePermission] = []
    
    def get(self, request, format=None, **kwargs):
        trivia = Trivia.objects.filter(is_public=True).order_by('?')[:1]
        serializer_trivia = TriviaSerializer(trivia, many=True)
        return Response(serializer_trivia.data)

class TriviaListCreateView(generics.ListCreateAPIView):
    serializer_class = TriviaSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Trivia.objects.filter(is_public=True)
        if user.role == 'admin':
            return Trivia.objects.all()
        return Trivia.objects.filter(
            models.Q(is_public=True) | 
            models.Q(user=user.created_by)
        )

    def perform_create(self, serializer):
        if not self.request.user.role == 'admin':
            raise permissions.PermissionDenied("Only admins can create trivia")
        serializer.save(user=self.request.user)

class TriviaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TriviaSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Trivia.objects.filter(is_public=True)
        if user.role == 'admin':
            return Trivia.objects.all()
        return Trivia.objects.filter(
            models.Q(is_public=True) | 
            models.Q(user=user.created_by)
        )

    def perform_update(self, serializer):
        if not self.request.user.role == 'admin':
            raise permissions.PermissionDenied("Only admins can edit trivia")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.role == 'admin':
            raise permissions.PermissionDenied("Only admins can delete trivia")
        instance.delete()
