from django.contrib import admin
from .models import *

# Register your models here.
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Fields to display in the admin list view
    search_fields = ('name',)  # Fields to search in the admin list view

admin.site.register(Unit, UnitAdmin)

class QuizAdmin(admin.ModelAdmin):
    list_display = ('unit', 'title', 'description')  # Fields to display in the admin list view
    search_fields = ('unit', 'title', 'description')  # Fields to search in the admin list view

admin.site.register(Quiz, QuizAdmin)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'correct_answer', 'quiz')  # Fields to display in the admin list view
    search_fields = ('question_text', 'question_type','quiz')  # Fields to search in the admin list view

admin.site.register(Question, QuestionAdmin)



class OptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'option_text')  # Fields to display in the admin list view
    search_fields = ('option_text',)  # Fields to search in the admin list view

admin.site.register(Option, OptionAdmin)

class LessonAdmin(admin.ModelAdmin):
    list_display = ('unit', 'content', 'difficulty')  # Fields to display in the admin list view
    search_fields = ('unit', 'difficulty')  # Fields to search in the admin list view

admin.site.register(Lesson, LessonAdmin)

class UserAttemptAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'questions_answered', 'user', 'attempt_date')  # Fields to display in the admin list view
    search_fields = ('quiz', 'user')  # Fields to search in the admin list view

admin.site.register(UserAttempts, UserAttemptAdmin)


class WordAdmin(admin.ModelAdmin):
    list_display = ('portuguese_word', 'english_translation', 'lesson',)  # Fields to display in the admin list view
    search_fields = ('portuguese_word', 'english_translation')  # Fields to search in the admin list view

admin.site.register(Word, WordAdmin)






