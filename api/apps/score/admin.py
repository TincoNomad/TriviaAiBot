from django.contrib import admin

from . import models

@admin.register(models.Score)

class ScoreAdmin(admin.ModelAdmin):
    list_display = [
        'name','points',
        'leaderboard',
        'created_at'
    ] 
    list_filter = ['leaderboard__discord_channel']
    search_fields = ['name', 'leaderboard__discord_channel']

@admin.register(models.LeaderBoard)

class LeaderBoardAdmin(admin.ModelAdmin):
    list_display = [
        'discord_channel',
        'created_by',
        'created_at'
    ]
    search_fields = ['discord_channel']
    list_filter = ['created_at']
