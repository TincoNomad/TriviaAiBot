from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Course
from .serializers import CourseSerializer

class RandomQuestions(APIView):

    def get(self, request, format=None, **kwargs):
        course = Course.objects.filter().order_by()
        serializerCourse = CourseSerializer(course, many= True)
        return Response(serializerCourse.data)