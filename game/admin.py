from django.contrib import admin
from .models import *

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'character_type')

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_points', 'reputation')

@admin.register(ClinicalTrial)
class ClinicalTrialAdmin(admin.ModelAdmin):
    list_display = ('name', 'player', 'status', 'current_participants', 'target_participants')

@admin.register(ResearchUpgrade)
class ResearchUpgradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'multiplier_bonus')

@admin.register(StoryChapter)
class StoryChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'required_level')

@admin.register(PatientStory)
class PatientStoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'condition', 'chapter')

@admin.register(StoryMission)
class StoryMissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter', 'target_participants', 'min_success_rate') 