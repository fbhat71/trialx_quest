from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('character/', views.character_selection, name='character_selection'),
    path('trial/new/', views.start_trial, name='start_trial'),
    path('trial/<int:trial_id>/', views.trial_detail, name='trial_detail'),
    path('trial/<int:trial_id>/recruit/', views.recruit_participants, name='recruit_participants'),
    path('research/', views.research_lab, name='research_lab'),
    path('story/', views.story_mode, name='story_mode'),
    path('story/chapter/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('story/mission/<int:mission_id>/', views.start_story_mission, name='start_story_mission'),
    path('api/patient-story/<int:patient_id>/', views.patient_story_detail, name='patient_story_detail'),
    path('trial/<int:trial_id>/puzzle/', views.recruitment_puzzle, name='recruitment_puzzle'),
    path('achievements/', views.achievements, name='achievements'),
    path('resources/', views.resources, name='resources'),
    path('resources/<int:resource_id>/', views.view_resource, name='view_resource'),
] 