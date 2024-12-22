from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Character(models.Model):
    TYPE_CHOICES = [
        ('DOCTOR', 'Doctor'),
        ('SCIENTIST', 'Scientist'),
        ('VOLUNTEER', 'Patient Volunteer'),
    ]
    
    name = models.CharField(max_length=100)
    character_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    ability_description = models.TextField()
    recruitment_bonus = models.IntegerField(default=0)
    data_analysis_bonus = models.IntegerField(default=0)
    patient_care_bonus = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.character_type}"

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.SET_NULL, null=True)
    experience_points = models.IntegerField(default=0)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=100000)
    reputation = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50
    )
    research_points = models.IntegerField(default=0)
    research_multiplier = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal('1.00')
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def add_research_points(self, base_points):
        """Add research points with multiplier"""
        self.research_points += int(base_points * self.research_multiplier)
        self.save()

class ClinicalTrial(models.Model):
    STATUS_CHOICES = [
        ('PLANNING', 'Planning Phase'),
        ('RECRUITING', 'Recruiting'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    target_participants = models.IntegerField()
    current_participants = models.IntegerField(default=0)
    budget_allocated = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    start_date = models.DateTimeField(auto_now_add=True)
    success_rate = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )

class Participant(models.Model):
    trial = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    condition = models.CharField(max_length=100)
    is_placebo = models.BooleanField(default=False)
    dropout_risk = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    satisfaction = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=50
    )

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/')
    requirement = models.TextField()

class PlayerBadge(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True) 

class ResearchUpgrade(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.IntegerField()
    multiplier_bonus = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    recruitment_bonus = models.IntegerField(default=0)
    analysis_bonus = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class PlayerUpgrade(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    upgrade = models.ForeignKey(ResearchUpgrade, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['player', 'upgrade']

class StoryChapter(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_level = models.IntegerField(default=1)
    required_reputation = models.IntegerField(default=0)
    order = models.IntegerField(unique=True)
    
    def __str__(self):
        return f"Chapter {self.order}: {self.title}"

class PatientStory(models.Model):
    CONDITION_CHOICES = [
        ('CANCER', 'Cancer Treatment'),
        ('RARE', 'Rare Disease'),
        ('CHRONIC', 'Chronic Condition'),
        ('MENTAL', 'Mental Health'),
        ('VACCINE', 'Vaccine Trial'),
    ]
    
    chapter = models.ForeignKey(StoryChapter, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    background = models.TextField()
    motivation = models.TextField()
    success_outcome = models.TextField()
    failure_outcome = models.TextField()
    
    def __str__(self):
        return f"{self.name}'s Story ({self.get_condition_display()})"

class StoryProgress(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    chapter = models.ForeignKey(StoryChapter, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    current_patient = models.ForeignKey(PatientStory, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        unique_together = ['player', 'chapter']

class StoryMission(models.Model):
    chapter = models.ForeignKey(StoryChapter, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_participants = models.IntegerField()
    min_success_rate = models.IntegerField()
    reward_xp = models.IntegerField()
    reward_reputation = models.IntegerField()
    reward_research_points = models.IntegerField()
    
    def __str__(self):
        return f"{self.chapter.title} - {self.title}"

class TrialEvent(models.Model):
    EVENT_TYPES = [
        ('SIDE_EFFECT', 'Side Effect Reported'),
        ('DROPOUT', 'Participant Dropout'),
        ('COMPLICATION', 'Medical Complication'),
        ('BREAKTHROUGH', 'Positive Breakthrough'),
    ]
    
    trial = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    severity = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.trial.name}"

class TrialDesign(models.Model):
    trial = models.OneToOneField(ClinicalTrial, on_delete=models.CASCADE)
    placebo_ratio = models.FloatField(default=0.5)  # Percentage of participants receiving placebo
    double_blind = models.BooleanField(default=True)
    follow_up_period = models.IntegerField(default=30)  # Days
    safety_protocols = models.TextField()
    ethical_considerations = models.TextField()
    
    def calculate_quality_score(self):
        """Calculate a score based on trial design quality"""
        score = 50  # Base score
        if self.double_blind:
            score += 20
        if self.safety_protocols:
            score += 15
        if self.ethical_considerations:
            score += 15
        return min(100, score)

class RecruitmentPuzzle(models.Model):
    PUZZLE_TYPES = [
        ('MATCH', 'Match Criteria'),
        ('QUIZ', 'Medical Knowledge Quiz'),
        ('ETHICS', 'Ethical Scenario'),
    ]
    
    puzzle_type = models.CharField(max_length=20, choices=PUZZLE_TYPES)
    question = models.TextField()
    correct_answer = models.TextField()
    difficulty = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    points_reward = models.IntegerField(default=100)
    
    def __str__(self):
        return f"{self.get_puzzle_type_display()} (Level {self.difficulty})"

class PuzzleOption(models.Model):
    puzzle = models.ForeignKey(RecruitmentPuzzle, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

class PlayerPuzzleProgress(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(RecruitmentPuzzle, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['player', 'puzzle']

class Achievement(models.Model):
    """Achievements are special rewards for major milestones"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/')
    points = models.IntegerField(default=100)
    requirement_type = models.CharField(max_length=50)  # e.g., 'trials_completed', 'participants_recruited'
    requirement_value = models.IntegerField()  # The value needed to earn this achievement
    
    def __str__(self):
        return self.name

class PlayerAchievement(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['player', 'achievement']