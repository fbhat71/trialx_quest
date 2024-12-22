from django.db import migrations

def create_initial_upgrades(apps, schema_editor):
    ResearchUpgrade = apps.get_model('game', 'ResearchUpgrade')
    
    upgrades = [
        {
            'name': 'Advanced Recruitment Techniques',
            'description': 'Improve your participant recruitment success rate',
            'cost': 1000,
            'recruitment_bonus': 10,
        },
        {
            'name': 'Data Analysis Software',
            'description': 'Better tools for analyzing trial data',
            'cost': 1500,
            'analysis_bonus': 15,
        },
        {
            'name': 'Research Efficiency',
            'description': 'Earn more research points from successful trials',
            'cost': 2000,
            'multiplier_bonus': 0.25,
        },
        {
            'name': 'Advanced Statistics',
            'description': 'Significantly improve trial success rates',
            'cost': 3000,
            'analysis_bonus': 25,
        },
    ]
    
    for upgrade in upgrades:
        ResearchUpgrade.objects.create(**upgrade)

def reverse_initial_upgrades(apps, schema_editor):
    ResearchUpgrade = apps.get_model('game', 'ResearchUpgrade')
    ResearchUpgrade.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_upgrades, reverse_initial_upgrades),
    ] 