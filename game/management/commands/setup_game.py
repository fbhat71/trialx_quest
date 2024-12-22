from django.core.management.base import BaseCommand
from django.apps import apps
from game.models import Character

class Command(BaseCommand):
    help = 'Sets up initial game data'

    def handle(self, *args, **kwargs):
        # Create character types
        self.stdout.write('Creating characters...')
        characters = [
            {
                'name': 'Dr. Sarah Chen',
                'character_type': 'DOCTOR',
                'ability_description': 'Skilled in patient care and recruitment. +10% recruitment success rate.',
                'recruitment_bonus': 10,
                'data_analysis_bonus': 5,
                'patient_care_bonus': 15,
            },
            {
                'name': 'Prof. James Wilson',
                'character_type': 'SCIENTIST',
                'ability_description': 'Expert in data analysis. +15% trial success rate.',
                'recruitment_bonus': 5,
                'data_analysis_bonus': 15,
                'patient_care_bonus': 5,
            },
            {
                'name': 'Maria Rodriguez',
                'character_type': 'VOLUNTEER',
                'ability_description': 'Experienced patient advocate. +10% patient satisfaction.',
                'recruitment_bonus': 15,
                'data_analysis_bonus': 0,
                'patient_care_bonus': 10,
            },
        ]
        
        for char_data in characters:
            Character.objects.get_or_create(
                name=char_data['name'],
                defaults=char_data
            )

        # Get model references
        RecruitmentPuzzle = apps.get_model('game', 'RecruitmentPuzzle')
        PuzzleOption = apps.get_model('game', 'PuzzleOption')
        StoryChapter = apps.get_model('game', 'StoryChapter')
        PatientStory = apps.get_model('game', 'PatientStory')
        StoryMission = apps.get_model('game', 'StoryMission')
        
        # Create puzzles
        puzzles = [
            {
                'type': 'QUIZ',
                'question': 'What is the main purpose of informed consent in clinical trials?',
                'answer': 'To ensure participants understand and voluntarily agree to the trial procedures and risks',
                'difficulty': 1,
                'points': 100
            },
            {
                'type': 'ETHICS',
                'question': 'A potential participant is eager to join the trial but doesn\'t fully understand English. What should you do?',
                'answer': 'Provide information in their native language and use a certified translator',
                'difficulty': 2,
                'points': 150
            },
            {
                'type': 'MATCH',
                'question': 'Match the participant with the appropriate trial criteria',
                'answer': 'Include based on matching all criteria',
                'difficulty': 3,
                'points': 200,
                'options': [
                    'Age 25-45, No pre-existing conditions',
                    'Age 46-65, Controlled diabetes',
                    'Age 18-30, History of condition',
                    'Age 31-50, First diagnosis'
                ]
            }
        ]
        
        for puzzle_data in puzzles:
            puzzle = RecruitmentPuzzle.objects.create(
                puzzle_type=puzzle_data['type'],
                question=puzzle_data['question'],
                correct_answer=puzzle_data['answer'],
                difficulty=puzzle_data['difficulty'],
                points_reward=puzzle_data['points']
            )
            
            if 'options' in puzzle_data:
                for option in puzzle_data['options']:
                    PuzzleOption.objects.create(
                        puzzle=puzzle,
                        text=option,
                        is_correct=(option == puzzle_data['answer'])
                    )

        # Create first chapter
        chapter1, _ = StoryChapter.objects.get_or_create(
            order=1,
            defaults={
                'title': "First Steps in Clinical Research",
                'description': "Begin your journey in clinical trials management with a small-scale study.",
                'required_level': 1,
                'required_reputation': 0,
            }
        )

        PatientStory.objects.get_or_create(
            name="Sarah Johnson",
            chapter=chapter1,
            defaults={
                'condition': "CANCER",
                'background': "Sarah is a 45-year-old mother of two...",
                'motivation': "After traditional treatments failed...",
                'success_outcome': "The trial showed promising results...",
                'failure_outcome': "While the treatment wasn't successful..."
            }
        )
        
        StoryMission.objects.get_or_create(
            title="First Steps",
            chapter=chapter1,
            defaults={
                'description': "Conduct your first trial with guidance...",
                'target_participants': 5,
                'min_success_rate': 60,
                'reward_xp': 500,
                'reward_reputation': 10,
                'reward_research_points': 100
            }
        )

        # Get Achievement model
        Achievement = apps.get_model('game', 'Achievement')
        
        # Create initial achievements
        achievements = [
            {
                'name': 'First Steps',
                'description': 'Complete your first clinical trial',
                'points': 100,
                'requirement_type': 'trials_completed',
                'requirement_value': 1
            },
            {
                'name': 'Recruitment Master',
                'description': 'Successfully recruit 50 participants',
                'points': 200,
                'requirement_type': 'participants_recruited',
                'requirement_value': 50
            },
            {
                'name': 'Perfect Trial',
                'description': 'Complete a trial with 100% success rate',
                'points': 500,
                'requirement_type': 'perfect_trials',
                'requirement_value': 1
            }
        ]
        
        for achievement_data in achievements:
            Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully set up game data')) 