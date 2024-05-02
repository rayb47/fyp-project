from django.db import models
from login.models import *
from django.utils import timezone

class Unit(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Quiz(models.Model):
    DIFFICULTY_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    difficulty = models.CharField(max_length=12, choices=DIFFICULTY_CHOICES, default='Beginner')

    def __str__(self):
        return self.title
    
class Question(models.Model):
    question_text = models.TextField()
    question_type = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)

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
    
class Word(models.Model):
    portuguese_word = models.CharField(max_length=255)
    english_translation = models.CharField(max_length=255)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.portuguese_word

    class Meta:
        ordering = ['id']

class Match(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    left_option = models.CharField(max_length=255)
    right_option = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.left_option} - {self.right_option}"
    
    class Meta:
        ordering = ['id']

class ExampleUsage(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='example_usages')
    english_usage = models.TextField()
    portuguese_usage = models.TextField()

    def __str__(self):
        return f'Usage of "{self.word.portuguese_word}" / "{self.word.english_translation}"'
    
class UserSavedWords(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    custom_english = models.CharField(max_length=255, null=True, blank=True)
    custom_portuguese = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.word:
            return f"{self.user.username} saved {self.word.portuguese_word}"
        else:
            return f"{self.user.username} saved {self.custom_english}"

class UserAttempts(models.Model):

    quiz = models.ForeignKey('Quiz', on_delete=models.SET_NULL, null=True, blank=True, related_name='attempts')
    lesson = models.ForeignKey('Lesson', on_delete=models.SET_NULL, null=True, blank=True, related_name='attempts')
    questions_answered = models.IntegerField(null=True, blank=True)
    pages_covered = models.IntegerField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attempts')
    attempt_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt {self.id} by User {self.user_id}"
    
    class Meta:
        verbose_name_plural = "User Attempts"

class UserAnswers(models.Model):
    # Replace 'Attempt' and 'Question' with your actual model names for attempts and questions
    attempt = models.ForeignKey('UserAttempts', on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='user_answers')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_answers')
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    answer_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user.username}'s answer for question {self.question_id}"

    class Meta:
        verbose_name_plural = "User Answers"


class UserActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    date = models.DateField(default=timezone.now)
    duration = models.DurationField(default=timezone.timedelta)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.duration}"


class UserFeedback(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="User")
    feedback = models.TextField(verbose_name="Feedback")

    def __str__(self):
        return f"Feedback from {self.user.username}"

    
    

