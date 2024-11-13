from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings
import uuid

class LeaderBoard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discord_channel = models.CharField(_('Discord Channel'), max_length=255, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leaderboards',
        verbose_name=_('Created By')
    )
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)

    def __str__(self):
        return f"Leaderboard - {self.discord_channel}"

    class Meta:
        verbose_name = _('LeaderBoard')
        verbose_name_plural = _('LeaderBoards')

class Score(models.Model):
    name = models.CharField(_('name'), max_length=255)
    points = models.IntegerField(_('points'))
    leaderboard = models.ForeignKey(
        LeaderBoard,
        on_delete=models.CASCADE,
        related_name='scores',
        verbose_name=_('LeaderBoard')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='scores', 
        verbose_name=_('User')
    )
    created_at = models.DateTimeField(_('Created'), auto_now_add=True)

    class Meta:
        ordering = ['-points']

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
