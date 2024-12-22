# Generated by Django 4.2.17 on 2024-12-22 10:26

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_story_content'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecruitmentPuzzle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puzzle_type', models.CharField(choices=[('MATCH', 'Match Criteria'), ('QUIZ', 'Medical Knowledge Quiz'), ('ETHICS', 'Ethical Scenario')], max_length=20)),
                ('question', models.TextField()),
                ('correct_answer', models.TextField()),
                ('difficulty', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('points_reward', models.IntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name='TrialEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('SIDE_EFFECT', 'Side Effect Reported'), ('DROPOUT', 'Participant Dropout'), ('COMPLICATION', 'Medical Complication'), ('BREAKTHROUGH', 'Positive Breakthrough')], max_length=20)),
                ('description', models.TextField()),
                ('severity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('trial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.clinicaltrial')),
            ],
        ),
        migrations.CreateModel(
            name='TrialDesign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placebo_ratio', models.FloatField(default=0.5)),
                ('double_blind', models.BooleanField(default=True)),
                ('follow_up_period', models.IntegerField(default=30)),
                ('safety_protocols', models.TextField()),
                ('ethical_considerations', models.TextField()),
                ('trial', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='game.clinicaltrial')),
            ],
        ),
        migrations.CreateModel(
            name='PuzzleOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('is_correct', models.BooleanField(default=False)),
                ('puzzle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.recruitmentpuzzle')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerPuzzleProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('attempts', models.IntegerField(default=0)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.playerprofile')),
                ('puzzle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.recruitmentpuzzle')),
            ],
            options={
                'unique_together': {('player', 'puzzle')},
            },
        ),
    ]