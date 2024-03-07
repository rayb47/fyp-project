from django.db import models

# Create your models here.
class Question(models.Model):
    question_text = models.TextField()
    question_type = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text