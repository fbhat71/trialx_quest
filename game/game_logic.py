import random
from datetime import timedelta
from django.utils import timezone

def calculate_recruitment_success(player_profile):
    """Calculate the chance of successfully recruiting a participant"""
    base_chance = 0.4  # 40% base chance
    
    # Handle case where character doesn't exist
    if player_profile.character:
        bonus = player_profile.character.recruitment_bonus / 100
    else:
        bonus = 0
        
    reputation_factor = player_profile.reputation / 200  # Max 0.5 bonus from reputation
    
    return min(0.9, base_chance + bonus + reputation_factor)

def process_trial_progress(trial):
    """Process daily trial progress and events"""
    if trial.status not in ['RECRUITING', 'ONGOING']:
        return
    
    # Check for participant dropouts
    for participant in trial.participant_set.all():
        dropout_roll = random.random()
        if dropout_roll < (participant.dropout_risk / 100):
            participant.delete()
            trial.current_participants -= 1
            
    # Update trial status based on conditions
    if trial.current_participants == 0 and trial.status == 'ONGOING':
        trial.status = 'FAILED'
        trial.save()
        return
        
    if trial.current_participants >= trial.target_participants:
        trial.status = 'ONGOING'
        
    # Calculate and update success rate
    if trial.status == 'ONGOING':
        base_success = 50
        player = trial.player
        data_bonus = player.character.data_analysis_bonus
        care_bonus = player.character.patient_care_bonus
        reputation_bonus = player.reputation / 2
        
        trial.success_rate = min(100, base_success + data_bonus + care_bonus + reputation_bonus)
        
    trial.save()

def award_experience(player_profile, amount):
    """Award experience points to player and handle level-ups"""
    player_profile.experience_points += amount
    
    # Every 1000 XP increases reputation by 5
    reputation_increase = (amount // 1000) * 5
    player_profile.reputation = min(100, player_profile.reputation + reputation_increase)
    
    player_profile.save()

def check_for_badges(player_profile):
    """Check and award any badges the player has earned"""
    from .models import Badge, PlayerBadge
    
    all_badges = Badge.objects.all()
    for badge in all_badges:
        if not PlayerBadge.objects.filter(player=player_profile, badge=badge).exists():
            if evaluate_badge_requirement(player_profile, badge):
                PlayerBadge.objects.create(player=player_profile, badge=badge)

def evaluate_badge_requirement(player_profile, badge):
    """Evaluate if a player meets a badge's requirements"""
    # Example requirements
    if badge.name == "Recruitment Master":
        successful_recruitments = player_profile.clinicaltrial_set.filter(
            current_participants__gte=10
        ).count()
        return successful_recruitments >= 5
        
    if badge.name == "Perfect Trial":
        perfect_trials = player_profile.clinicaltrial_set.filter(
            status='COMPLETED',
            success_rate__gte=90
        ).count()
        return perfect_trials >= 1
    
    return False 

def award_research_points(player_profile, trial):
    """Award research points based on trial success"""
    if trial.status != 'COMPLETED':
        return
    
    base_points = trial.target_participants * 10
    success_bonus = int(trial.success_rate / 10)
    total_base_points = base_points + success_bonus
    
    player_profile.add_research_points(total_base_points)
    
def apply_upgrade(player_profile, upgrade_id):
    """Apply a research upgrade to a player"""
    try:
        upgrade = ResearchUpgrade.objects.get(id=upgrade_id)
        if player_profile.research_points >= upgrade.cost:
            PlayerUpgrade.objects.create(player=player_profile, upgrade=upgrade)
            player_profile.research_points -= upgrade.cost
            player_profile.research_multiplier += upgrade.multiplier_bonus
            player_profile.character.recruitment_bonus += upgrade.recruitment_bonus
            player_profile.character.data_analysis_bonus += upgrade.analysis_bonus
            player_profile.save()
            player_profile.character.save()
            return True
    except ResearchUpgrade.DoesNotExist:
        pass
    return False 