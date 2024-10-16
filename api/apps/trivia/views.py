from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import TriviaSerializer, ThemeSerializer
from rest_framework import generics, permissions
from .models import Trivia, Theme

class ThemeListView(generics.ListAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

class RandomQuestions(APIView):
    def get(self, request, format=None, **kwargs):
        trivia = Trivia.objects.all().order_by('?')[:1]
        serializer_trivia = TriviaSerializer(trivia, many=True)
        return Response(serializer_trivia.data)

class TriviaListCreateView(generics.ListCreateAPIView):
    queryset = Trivia.objects.all()
    serializer_class = TriviaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TriviaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trivia.objects.all()
    serializer_class = TriviaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
