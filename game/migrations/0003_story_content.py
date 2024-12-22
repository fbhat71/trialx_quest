from django.db import migrations

def create_story_content(apps, schema_editor):
    StoryChapter = apps.get_model('game', 'StoryChapter')
    PatientStory = apps.get_model('game', 'PatientStory')
    StoryMission = apps.get_model('game', 'StoryMission')
    
    # Create first chapter
    chapter1 = StoryChapter.objects.create(
        order=1,
        title="First Steps in Clinical Research",
        description="Begin your journey in clinical trials management with a small-scale study.",
        required_level=1,
        required_reputation=0,
    )

    PatientStory.objects.create(
        chapter=chapter1,
        name="Sarah Johnson",
        condition="CANCER",
        background="Sarah is a 45-year-old mother of two...",
        motivation="After traditional treatments failed...",
        success_outcome="The trial showed promising results...",
        failure_outcome="While the treatment wasn't successful..."
    )
    
    StoryMission.objects.create(
        chapter=chapter1,
        title="First Steps",
        description="Conduct your first trial with guidance...",
        target_participants=5,
        min_success_rate=60,
        reward_xp=500,
        reward_reputation=10,
        reward_research_points=100
    )

def reverse_story_content(apps, schema_editor):
    StoryChapter = apps.get_model('game', 'StoryChapter')
    StoryChapter.objects.all().delete()
    # This will cascade delete related PatientStory and StoryMission objects

class Migration(migrations.Migration):
    dependencies = [
        ('game', '0002_initial_upgrades'),
    ]

    operations = [
        migrations.RunPython(create_story_content, reverse_story_content),
    ] 