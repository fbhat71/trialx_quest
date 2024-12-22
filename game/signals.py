from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PlayerProfile, Character

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a default character if none exist
        default_character = Character.objects.first()
        if not default_character:
            default_character = Character.objects.create(
                name="Dr. Default",
                character_type="DOCTOR",
                ability_description="Basic character with standard abilities",
                recruitment_bonus=5,
                data_analysis_bonus=5,
                patient_care_bonus=5
            )
        
        PlayerProfile.objects.create(
            user=instance,
            character=default_character
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'playerprofile'):
        # Create a default character if none exist
        default_character = Character.objects.first()
        if not default_character:
            default_character = Character.objects.create(
                name="Dr. Default",
                character_type="DOCTOR",
                ability_description="Basic character with standard abilities",
                recruitment_bonus=5,
                data_analysis_bonus=5,
                patient_care_bonus=5
            )
            
        PlayerProfile.objects.create(
            user=instance,
            character=default_character
        )
    instance.playerprofile.save() 