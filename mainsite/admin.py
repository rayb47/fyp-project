from django.contrib import admin
from .models import *

# Register your models here.
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'description') 
    search_fields = ('name',) 

admin.site.register(Unit, UnitAdmin)

class QuizAdmin(admin.ModelAdmin):
    list_display = ('unit', 'title', 'description', 'difficulty') 
    search_fields = ('unit', 'title', 'description', 'difficulty') 

admin.site.register(Quiz, QuizAdmin)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'correct_answer', 'quiz')
    search_fields = ('question_text', 'question_type','quiz')

admin.site.register(Question, QuestionAdmin)

class OptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'option_text', 'translation') 
    search_fields = ('option_text',) 

admin.site.register(Option, OptionAdmin)

class LessonAdmin(admin.ModelAdmin):
    list_display = ('unit', 'content', 'difficulty') 
    search_fields = ('unit', 'difficulty') 

admin.site.register(Lesson, LessonAdmin)


class WordAdmin(admin.ModelAdmin):
    list_display = ('portuguese_word', 'english_translation', 'lesson',) 
    search_fields = ('portuguese_word', 'english_translation')

admin.site.register(Word, WordAdmin)

class MatchAdmin(admin.ModelAdmin):
    list_display = ('question', 'left_option', 'right_option',)
    search_fields = ('question', 'left_option', 'right_option',)

admin.site.register(Match, MatchAdmin)

class ExampleUsageAdmin(admin.ModelAdmin):
    list_display = ('word', 'english_usage', 'portuguese_usage',)
    search_fields = ('word', 'english_usage', 'portuguese_usage',)

admin.site.register(ExampleUsage, ExampleUsageAdmin)

class UserSavedWordsAdmin(admin.ModelAdmin):
    list_display = ('word', 'user', 'custom_english', 'custom_portuguese')
    search_fields = ('word', 'user', 'custom_english', 'custom_portuguese')

admin.site.register(UserSavedWords, UserSavedWordsAdmin)

class UserAttemptsAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'lesson', 'questions_answered', 'pages_covered', 'user', 'attempt_date')
    search_fields = ('quiz', 'lesson', 'questions_answered', 'pages_covered', 'user', 'attempt_date')

admin.site.register(UserAttempts, UserAttemptsAdmin)

class UserAnswersAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'user', 'answer_text', 'is_correct', 'answer_date')
    search_fields = ('attempt', 'question', 'user', 'answer_text', 'is_correct', 'answer_date') 

admin.site.register(UserAnswers, UserAnswersAdmin)

class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'duration')
    search_fields = ('user', 'date', 'duration')

admin.site.register(UserActivity, UserActivityAdmin)

admin.site.register(UserFeedback)





