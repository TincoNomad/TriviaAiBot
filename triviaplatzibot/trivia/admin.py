from django.contrib import admin

from . import models

#Table union Queastion + Answers
class AnswerInlineModel(admin.TabularInline):
    model = models.Answer
    fields = [
        'answerTitle',
        'is_correct',
        'question',
    ]
    extra = 0

#Table union Course + Question
class QuestionInLineModel(admin.TabularInline):
    model = models.Question
    fields = [
        'questionTitle',
        'points',
    ]
    extra = 0

#Cursos
@admin.register(models.Course)

class CourseAdmin(admin.ModelAdmin):
    fields = [
        'title',
        'difficulty',
        'school',
        'url',
    ]
    list_display =[
        'title',
        'difficulty',
        'school',
    ]
    inlines = [QuestionInLineModel,]

#Qestion
@admin.register(models.Question)

class QuestionAdmin(admin.ModelAdmin):
    fields = [
        'questionTitle',
        'points',
    
    ]
    list_display = [
        'questionTitle',
        'course',
        'updated_at',
    ]
    inlines = [AnswerInlineModel,]

#Answer
@admin.register(models.Answer)

class AnswerAdmin(admin.ModelAdmin):
    list_display = [
        'answerTitle',
        'is_correct',
        'question',
    ]
    