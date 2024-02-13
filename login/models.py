from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class CustomUser(AbstractUser):
    # Additional fields as per your table
    proficiency_level = models.IntegerField(choices=[(1, 'Beginner'), (2, 'Intermediate'), (3, 'Advanced')], null=True, blank=True)
    study_frequency = models.TextField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly')], null=True, blank=True)
    study_frequency_amount = models.IntegerField(help_text="Time in hours", null=True, blank=True)
    portuguese_default = models.BooleanField(default=False, help_text="Is Portuguese set as the default language", blank=True)

    def __str__(self):
        return self.username