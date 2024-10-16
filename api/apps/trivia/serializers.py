#for take the information form the data base and converted into a format the bot can use 

from rest_framework import serializers
from .models import Question, Answer, Trivia, Theme

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ['id', 'name']

class AnswerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Answer
        fields = ['id', 'answer_title', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'points', 'answers']

class TriviaSerializer(serializers.ModelSerializer):
    theme = serializers.CharField(max_length=100)
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Trivia
        fields = ['id', 'title', 'difficulty', 'theme', 'url', 'questions']

    def create(self, validated_data):
        theme_data = validated_data.pop('theme', None)
        theme = None

        if theme_data:
            if isinstance(theme_data, int):
                theme = Theme.objects.get(id=theme_data)
            else:
                theme, _ = Theme.objects.get_or_create(name=theme_data)

        trivia = Trivia.objects.create(theme=theme, **validated_data)
        return trivia

    def update(self, instance, validated_data):
        # ... (código anterior) ...

        if 'questions' in validated_data:
            self.update_questions(instance, validated_data.pop('questions'))

        instance.save()
        return instance

    def update_questions(self, instance, questions_data):
        for question_data in questions_data:
            question_id = question_data.get('id')
            if question_id:
                question = Question.objects.get(id=question_id, trivia=instance)
                for attr, value in question_data.items():
                    if attr != 'answers':
                        setattr(question, attr, value)
                question.save()
                if 'answers' in question_data:
                    self.update_answers(question, question_data['answers'])
            else:
                new_question = Question.objects.create(trivia=instance, **question_data)
                if 'answers' in question_data:
                    self.create_answers(new_question, question_data['answers'])

    def update_answers(self, question, answers_data):
        for answer_data in answers_data:
            answer_id = answer_data.get('id')
            if answer_id:
                answer = Answer.objects.get(id=answer_id, question=question)
                for attr, value in answer_data.items():
                    setattr(answer, attr, value)
                answer.save()
            else:
                Answer.objects.create(question=question, **answer_data)
