from django.contrib import admin

from . import models

#Table union Question + Answers
class AnswerInlineModel(admin.TabularInline):
    model = models.Answer
    fields = [
        'answer_title',
        'is_correct',
    ]
    extra = 0

#Table union Trivia + Question
class QuestionInLineModel(admin.TabularInline):
    model = models.Question
    fields = [
        'question_title',
    ]
    extra = 0

#Trivias
@admin.register(models.Trivia)
class TriviaAdmin(admin.ModelAdmin):
    fields = [
        'title',
        'difficulty',
        'theme',
        'url',
    ]
    list_display = [
        'title',
        'difficulty',
        'theme',
    ]
    inlines = [QuestionInLineModel,]

#Themes
@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name']

#Questions
@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = [
        'trivia',
        'question_title',
    ]
    list_display = [
        'question_title',
        'trivia',
        'updated_at',
    ]
    inlines = [AnswerInlineModel,]

#Answers
@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = [
        'answer_title',
        'is_correct',
        'question',
    ]
    
