from django.db import models
from login.models import *

# Create your models here.
class Unit(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Quiz(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)  # Can be null or blank
    #     created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Question(models.Model):
    question_text = models.TextField()
    question_type = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)  # Adding the quiz foreign key

    def __str__(self):
        return self.question_text
    
    class Meta:
        ordering = ['id']

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)

    def __str__(self):
        return self.option_text
    
class Lesson(models.Model):
    # unit.lessons.all()
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lessons')
    content = models.TextField()
    difficulty = models.CharField(max_length=12, choices=DIFFICULTY_CHOICES)

    def __str__(self):
        return f"{self.difficulty} lesson in {self.unit.name}"
    
class UserAttempts(models.Model):
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE)  # Use your actual Quiz model
    questions_answered = models.IntegerField(default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Assuming using Django's built-in User model
    attempt_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s attempt on {self.attempt_date.strftime('%Y-%m-%d %H:%M')}"
    
class Word(models.Model):
    portuguese_word = models.CharField(max_length=255)
    english_translation = models.CharField(max_length=255)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.portuguese_word

    class Meta:
        ordering = ['id']
    
    

