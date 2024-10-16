from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings

class Score(models.Model):
    name = models.CharField(_('name'), max_length=255)
    points = models.IntegerField(_('points'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scores', verbose_name=_('User'))

    def __str__(self):
        return f"{self.name} - {self.points}"

class TriviaWinner(models.Model):
    name = models.CharField(_('Winner Name'), max_length=255)
    trivia_name = models.CharField(_('Trivia Name'), max_length=255)
    date_won = models.DateTimeField(_('Date Won'), auto_now_add=True)
    score = models.CharField(_('Score'), max_length=100)

    def __str__(self):
        return f"{self.name} - {self.trivia_name} - {self.date_won}"

    class Meta:
        ordering = ['-date_won']
