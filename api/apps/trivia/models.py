from django.db import models
from django.utils.translation import gettext as _


# Course model representing different courses available
class Trivia(models.Model):
    LEVEL_DEFAULT = (0, _('-----'))
    
    title = models.CharField(_('Título'), max_length=250)
    difficulty = models.IntegerField(_('Dificultad'), default=0)
    theme = models.IntegerField(_('Tema'), default=0)
    url = models.URLField(_('URL'), null=True, blank=True)
    
    def __str__(self):
        return self.title

class Level(models.Model):
    value = models.IntegerField(_('Valor'))
    name = models.CharField(_('Nombre'), max_length=100)

    def __str__(self):
        return f"({self.value}, _('{self.name}'))"

class Theme(models.Model):
    value = models.IntegerField(_('Valor'))
    name = models.CharField(_('Nombre'), max_length=100)

    def __str__(self):
        return f"({self.value}, _('{self.name}'))"

# Question model representing questions for each course
class Question(models.Model):
    trivia = models.ForeignKey(Trivia, related_name='questions', verbose_name=_('Trivia'), on_delete=models.CASCADE, null=True)
    question_title = models.CharField(_('Question Title'), max_length=250, null=True)
    points = models.SmallIntegerField(_('Points'))
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)

    def __str__(self):
        return self.question_title

# Answer model representing answers for each question
class Answer(models.Model):
    trivia = models.ForeignKey(Trivia, related_name='answers', verbose_name=_('Trivia'), on_delete=models.CASCADE, null=True)
    question = models.ForeignKey(Question, related_name='answers', verbose_name=_('Question'), on_delete=models.CASCADE)
    answer_title = models.CharField(_('Answer Title'), max_length=2502, null=True)
    is_correct = models.BooleanField(_('Correct Answer'), default=False)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated'), auto_now=True)

    def __str__(self):
        return self.answer_title
