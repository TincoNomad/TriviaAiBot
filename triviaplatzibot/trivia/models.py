from email.policy import default
from random import choices
from django.db import models
from django.utils.translation import gettext as _

#QUESTIONS
class Question(models.Model):

    LEVEL = (
        (0,_('-----')),
        (1,_('Beginner')),
        (2,_('Intermediate')),
        (3,_('Advance')),
    )

    SCHOOLS = (
        (0,_('-----')),
        (1,_('developing')),
        (2,_('Data/M-Learning')),
        (3,_('marketing')),
        (4,_('design')),
        (5,_('soft skills')),
        (6,_('Business')),
        (7,_('Finanzas')),
        (8,_('digital Content')),
        (9,_('startup')),
        (10,_('english')),
    )

    title = models.CharField(_('title'), max_length=250)
    points = models.SmallIntegerField(_('Points'))
    difficulty = models.IntegerField(_('Difficulty'), choices=LEVEL, default=0)
    schools = models.IntegerField(_('Schools'), choices=SCHOOLS, default=0)
    url = models.URLField(_('url'),null=True, default='')
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('created'), auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True, auto_now_add=False)

    def __str__(Self):
        return Self.title

#ANSWERS     
class Answer(models.Model):

    question = models.ForeignKey(Question, related_name='answer', verbose_name=_('Question'), on_delete=models.CASCADE)
    answer = models.CharField(_('Answer'), max_length=250)
    is_correct = models.BooleanField(_('Correct Answer'), default=False)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('created'), auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True, auto_now_add=False)

    def __str__(Self):
        return Self.answer