from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
import random
from .models import *
from .game_logic import (
    calculate_recruitment_success, process_trial_progress,
    award_experience, check_for_badges, apply_upgrade
)
from django.utils import timezone

@login_required
def dashboard(request):
    profile, created = PlayerProfile.objects.get_or_create(
        user=request.user
    )
    
    # Redirect to character selection if no character chosen
    if not profile.character:
        messages.info(request, "Please choose your character first!")
        return redirect('character_selection')
    
    active_trials = ClinicalTrial.objects.filter(
        player=profile,
        status__in=['PLANNING', 'RECRUITING', 'ONGOING']
    )
    return render(request, 'game/dashboard.html', {
        'profile': profile,
        'active_trials': active_trials
    })

@login_required
def start_trial(request):
    if request.method == 'POST':
        profile = PlayerProfile.objects.get(user=request.user)
        trial = ClinicalTrial.objects.create(
            player=profile,
            name=request.POST['name'],
            description=request.POST['description'],
            target_participants=int(request.POST['target_participants']),
            budget_allocated=float(request.POST['budget'])
        )
        return redirect('trial_detail', trial_id=trial.id)
    return render(request, 'game/start_trial.html')

@login_required
def recruit_participants(request, trial_id):
    trial = get_object_or_404(ClinicalTrial, id=trial_id)
    success_chance = calculate_recruitment_success(request.user.playerprofile)
    
    if request.method == 'POST':
        # Logic for recruiting participants
        if success_chance > random.random():
            Participant.objects.create(
                trial=trial,
                name=request.POST['name'],
                age=request.POST['age'],
                condition=request.POST['condition']
            )
            trial.current_participants += 1
            trial.save()
            return JsonResponse({
                'success': True,
                'message': 'Successfully recruited participant!'
            })
        return JsonResponse({
            'success': False,
            'message': 'Failed to recruit participant. Try again!'
        })
    
    return render(request, 'game/recruit.html', {
        'trial': trial,
        'recruitment_chance': success_chance * 100  # Show percentage
    })

@login_required
def process_trial(request, trial_id):
    trial = get_object_or_404(ClinicalTrial, id=trial_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'analyze_data':
            success_chance = (trial.success_rate / 100) * random.random()
            if success_chance > 0.5:
                trial.status = 'COMPLETED'
                award_experience(trial.player, 1000)
            else:
                trial.status = 'FAILED'
                award_experience(trial.player, 200)
            
            trial.save()
            check_for_badges(trial.player)
            
            return JsonResponse({
                'success': trial.status == 'COMPLETED',
                'message': f"Trial {trial.status.lower()}"
            })
    
    process_trial_progress(trial)
    return render(request, 'game/trial_detail.html', {'trial': trial})

@login_required
def research_lab(request):
    player = request.user.playerprofile
    
    if request.method == 'POST':
        upgrade_id = request.POST.get('upgrade_id')
        if apply_upgrade(player, upgrade_id):
            messages.success(request, "Upgrade purchased successfully!")
        else:
            messages.error(request, "Unable to purchase upgrade. Check your research points.")
        
        return redirect('research_lab')
    
    # Get all upgrades and mark which ones the player has
    all_upgrades = ResearchUpgrade.objects.all()
    purchased_upgrades = set(PlayerUpgrade.objects.filter(
        player=player
    ).values_list('upgrade_id', flat=True))
    
    for upgrade in all_upgrades:
        upgrade.is_purchased = upgrade.id in purchased_upgrades
    
    return render(request, 'game/research_lab.html', {
        'player': player,
        'available_upgrades': all_upgrades
    })

@login_required
def story_mode(request):
    player = request.user.playerprofile
    
    # Get all chapters and player's progress
    chapters = StoryChapter.objects.all().order_by('order')
    progress = StoryProgress.objects.filter(player=player)
    progress_dict = {p.chapter_id: p for p in progress}
    
    # Calculate player level (1 level per 1000 XP)
    player_level = (player.experience_points // 1000) + 1
    
    for chapter in chapters:
        chapter.progress = progress_dict.get(chapter.id)
        chapter.is_available = (
            player_level >= chapter.required_level and 
            player.reputation >= chapter.required_reputation
        )
    
    return render(request, 'game/story_mode.html', {
        'chapters': chapters,
        'player_level': player_level
    })

@login_required
def chapter_detail(request, chapter_id):
    player = request.user.playerprofile
    chapter = get_object_or_404(StoryChapter, id=chapter_id)
    
    # Get or create progress
    progress, created = StoryProgress.objects.get_or_create(
        player=player,
        chapter=chapter
    )
    
    # Get available missions
    missions = StoryMission.objects.filter(chapter=chapter)
    patient_stories = PatientStory.objects.filter(chapter=chapter)
    
    return render(request, 'game/chapter_detail.html', {
        'chapter': chapter,
        'progress': progress,
        'missions': missions,
        'patient_stories': patient_stories
    })

@login_required
def start_story_mission(request, mission_id):
    mission = get_object_or_404(StoryMission, id=mission_id)
    player = request.user.playerprofile
    
    if request.method == 'POST':
        # Create a special story-mode trial
        trial = ClinicalTrial.objects.create(
            player=player,
            name=mission.title,
            description=mission.description,
            target_participants=mission.target_participants,
            budget_allocated=50000  # Story missions have fixed budget
        )
        
        # Associate trial with story progress
        progress = StoryProgress.objects.get(player=player, chapter=mission.chapter)
        progress.current_trial = trial
        progress.save()
        
        return redirect('trial_detail', trial_id=trial.id)
    
    return render(request, 'game/start_story_mission.html', {'mission': mission})

@login_required
def patient_story_detail(request, patient_id):
    patient = get_object_or_404(PatientStory, id=patient_id)
    return JsonResponse({
        'name': patient.name,
        'condition': patient.get_condition_display(),
        'background': patient.background,
        'motivation': patient.motivation
    })

@login_required
def trial_detail(request, trial_id):
    trial = get_object_or_404(ClinicalTrial, id=trial_id)
    
    # Process trial progress
    process_trial_progress(trial)
    
    return render(request, 'game/trial_detail.html', {
        'trial': trial,
        'recruitment_chance': calculate_recruitment_success(request.user.playerprofile) * 100,
    })

@login_required
def character_selection(request):
    if request.method == 'POST':
        character_id = request.POST.get('character_id')
        character = get_object_or_404(Character, id=character_id)
        profile = request.user.playerprofile
        profile.character = character
        profile.save()
        return redirect('dashboard')
    
    characters = Character.objects.all()
    return render(request, 'game/character_selection.html', {
        'characters': characters
    })

@login_required
def design_trial(request, trial_id):
    trial = get_object_or_404(ClinicalTrial, id=trial_id)
    
    if request.method == 'POST':
        design = TrialDesign.objects.create(
            trial=trial,
            placebo_ratio=float(request.POST.get('placebo_ratio', 0.5)),
            double_blind=request.POST.get('double_blind') == 'on',
            follow_up_period=int(request.POST.get('follow_up_period', 30)),
            safety_protocols=request.POST.get('safety_protocols', ''),
            ethical_considerations=request.POST.get('ethical_considerations', '')
        )
        
        # Update trial status based on design quality
        quality_score = design.calculate_quality_score()
        if quality_score >= 80:
            trial.status = 'RECRUITING'
            messages.success(request, "Trial design approved! You can now start recruiting participants.")
        else:
            messages.warning(request, "Trial design needs improvement before recruitment can begin.")
        
        trial.save()
        return redirect('trial_detail', trial_id=trial.id)
    
    return render(request, 'game/design_trial.html', {'trial': trial})

@login_required
def recruitment_puzzle(request, trial_id):
    trial = get_object_or_404(ClinicalTrial, id=trial_id)
    player = request.user.playerprofile
    
    # Get a random unsolved puzzle
    completed_puzzles = PlayerPuzzleProgress.objects.filter(
        player=player, completed=True
    ).values_list('puzzle_id', flat=True)
    
    puzzle = RecruitmentPuzzle.objects.exclude(
        id__in=completed_puzzles
    ).order_by('?').first()
    
    if request.method == 'POST':
        answer = request.POST.get('answer')
        puzzle_id = request.POST.get('puzzle_id')
        puzzle = get_object_or_404(RecruitmentPuzzle, id=puzzle_id)
        
        progress, created = PlayerPuzzleProgress.objects.get_or_create(
            player=player,
            puzzle=puzzle
        )
        
        progress.attempts += 1
        
        if answer.lower() == puzzle.correct_answer.lower():
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()
            
            # Award points and potentially recruit a participant
            player.experience_points += puzzle.points_reward
            player.save()
            
            if random.random() < 0.8:  # 80% chance of recruitment after solving puzzle
                Participant.objects.create(
                    trial=trial,
                    name=f"Recruited via Puzzle #{puzzle.id}",
                    age=random.randint(18, 65),
                    condition=random.choice(['Condition A', 'Condition B', 'Condition C'])
                )
                trial.current_participants += 1
                trial.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Puzzle solved! New participant recruited!',
                    'points': puzzle.points_reward
                })
            
            return JsonResponse({
                'success': True,
                'message': 'Puzzle solved! Keep trying to recruit participants.',
                'points': puzzle.points_reward
            })
            
        return JsonResponse({
            'success': False,
            'message': 'Incorrect answer. Try again!'
        })
    
    return render(request, 'game/recruitment_puzzle.html', {
        'trial': trial,
        'puzzle': puzzle
    })

@login_required
def achievements(request):
    player = request.user.playerprofile
    
    # Get all achievements and mark which ones the player has earned
    all_achievements = Achievement.objects.all()
    earned_achievements = set(PlayerAchievement.objects.filter(
        player=player
    ).values_list('achievement_id', flat=True))
    
    for achievement in all_achievements:
        achievement.is_earned = achievement.id in earned_achievements
        if not achievement.is_earned:
            # Calculate progress
            if achievement.requirement_type == 'trials_completed':
                current = ClinicalTrial.objects.filter(
                    player=player, status='COMPLETED'
                ).count()
            elif achievement.requirement_type == 'participants_recruited':
                current = Participant.objects.filter(
                    trial__player=player
                ).count()
            else:
                current = 0
            
            achievement.progress = min(100, (current / achievement.requirement_value) * 100)
    
    return render(request, 'game/achievements.html', {
        'achievements': all_achievements
    })

@login_required
def resources(request):
    player = request.user.playerprofile
    
    # Get all resources and check which ones are unlocked
    all_resources = Resource.objects.all()
    unlocked_resources = set(PlayerResource.objects.filter(
        player=player
    ).values_list('resource_id', flat=True))
    
    for resource in all_resources:
        resource.is_unlocked = (
            resource.id in unlocked_resources or 
            player.experience_points >= resource.points_required
        )
        if resource.is_unlocked and resource.id not in unlocked_resources:
            PlayerResource.objects.create(player=player, resource=resource)
    
    return render(request, 'game/resources.html', {
        'resources': all_resources
    })

@login_required
def view_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    player = request.user.playerprofile
    
    # Check if player can access this resource
    if player.experience_points < resource.points_required:
        messages.error(request, "You need more experience points to access this resource.")
        return redirect('resources')
    
    # Mark as viewed
    player_resource, created = PlayerResource.objects.get_or_create(
        player=player, resource=resource
    )
    if not player_resource.has_viewed:
        player_resource.has_viewed = True
        player_resource.save()
    
    return render(request, 'game/view_resource.html', {
        'resource': resource
    }) 