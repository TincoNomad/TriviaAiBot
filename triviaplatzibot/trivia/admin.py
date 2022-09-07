from django.contrib import admin

from . import models


#Table union Queastion + Answers
class AnswweInlineModel(admin.TabularInline):
    model = models.Answer
    fields = [
        'answer',
        'is_correct',
    ]

#Qestion
@admin.register(models.Question)

class QustionAdmin(admin.ModelAdmin):
    fields = [
        'title',
        'points',
        'difficulty',
    ]
    list_display = [
        'title',
        'updated_at'
    ]
    inlines = [AnswweInlineModel,]


#Answer
@admin.register(models.Answer)

class AnswerAdmin(admin.ModelAdmin):
    list_display = [
        'answer',
        'is_correct',
        'question',
    ]
