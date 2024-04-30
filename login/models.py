from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    # Additional fields as per your table
    proficiency_level = models.IntegerField(choices=[(1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced')], null=True, blank=True)
    study_frequency = models.TextField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly')], null=True, blank=True)
    study_frequency_amount = models.IntegerField(help_text="Time in hours", null=True, blank=True)
    portuguese_default = models.BooleanField(default=False, help_text="Is Portuguese set as the default language", blank=True)
    daily_question_goal = models.IntegerField(default=0, help_text="Number of questions the user aims to answer each day")
    daily_activity_goal = models.IntegerField(default=0, help_text="Number of minutes the user aims to be active on the site each day")
    PLAYBACK_SPEED_CHOICES = [
        ('normal', 'Normal'),
        ('slow', 'Slow'),
        ('fast', 'Fast')
    ]
    playback_speed = models.CharField(max_length=6, choices=PLAYBACK_SPEED_CHOICES, default='normal', help_text="Preferred audio playback speed")
    def __str__(self):
        return self.username