#for take the information form the data base and converted into a format the bot can use 

from rest_framework import serializers
from .models import Question, Answer, Course

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            'id',
            'answerTitle',
            'is_correct',
        ]

class RandomQestionsSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'questionTitle',
            'answer',
            'points',
        ]

class CourseSerializer(serializers.ModelSerializer):
    question = RandomQestionsSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields= [
            'id',
            'title',
            'question',
            'difficulty',
            'school',
            'url',
        ]